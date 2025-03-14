# trips/views.py
import os
import requests
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TripSerializer

# In this implementation we use OpenRouteService (ORS) APIs.
# Make sure you set your ORS_API_KEY in the environment variables.
ORS_API_KEY = os.environ.get("ORS_API_KEY")
if not ORS_API_KEY:
    raise Exception("ORS_API_KEY not set in environment variables.")

def real_simulate_trip(current_loc, pickup_loc, dropoff_loc, cycle_used):
    """
    This function:
      1. Geocodes the provided addresses using the ORS geocoding API.
      2. Retrieves a driving route from current location to pickup to dropoff
         using the ORS directions API.
      3. Converts the distance (in meters) to miles.
      4. Simulates a timeline based on a fixed average speed (50 mph) and HOS rules:
         - A 1-hour pickup event at start.
         - Driving is simulated in 1-hour increments.
         - After 8 hours of driving, a 30-minute break is inserted.
         - If 11 hours of driving or 14 hours on-duty is reached, the day ends with a 10-hour rest.
         - Fueling stops are added every 1,000 miles.
         - A 1-hour dropoff event is appended at the end.
    Returns:
      - route_coords: List of coordinates (from geocoding) used in the route.
      - distance_miles: Total trip distance in miles.
      - fuel_stops: List of fueling stops.
      - daily_logs: List of daily log objects describing the timeline.
    """
    # --- Step 1: Geocode Addresses ---
    def geocode_address(address):
        geocode_url = "https://api.openrouteservice.org/geocode/search"
        params = {
            "api_key": ORS_API_KEY,
            "text": address,
            "size": 1
        }
        response = requests.get(geocode_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("features"):
                # Returns coordinates in [lng, lat] format
                return data["features"][0]["geometry"]["coordinates"]
        raise Exception(f"Geocoding failed for address: {address}")

    current_coords = geocode_address(current_loc)
    pickup_coords = geocode_address(pickup_loc)
    dropoff_coords = geocode_address(dropoff_loc)
    # Our route will be: current -> pickup -> dropoff
    route_coords = [current_coords, pickup_coords, dropoff_coords]

    # --- Step 2: Get Directions ---
    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": route_coords
    }
    dir_resp = requests.post(directions_url, json=body, headers=headers)
    if dir_resp.status_code != 200:
        raise Exception("Directions API error: " + dir_resp.text)
    directions_data = dir_resp.json()
    # For simplicity we return the input coordinates as the route.
    # (In production you might decode the polyline geometry.)
    summary = directions_data["routes"][0]["summary"]
    distance_meters = summary["distance"]
    distance_miles = distance_meters / 1609.34  # convert meters to miles

    # --- Step 3: Calculate Driving Time & Simulate HOS Events ---
    # Assume an average speed of 50 mph.
    average_speed = 50.0
    total_driving_hours = distance_miles / average_speed

    # Helper to format time as "HH:MM"
    def format_time(time_obj):
        return time_obj.strftime("%H:%M")

    daily_logs = []
    day_index = 1
    current_day_events = []
    # Assume each day starts at 06:00.
    day_start = datetime.strptime("06:00", "%H:%M")
    current_time = day_start
    on_duty_hours = 0.0
    driving_hours_today = 0.0
    remaining_driving = total_driving_hours

    # Fueling: add a fueling stop every 1000 miles.
    cumulative_miles = 0.0
    next_fuel_mile = 1000.0
    fuel_stops = []

    # --- Add Pickup Event (1 hour) ---
    pickup_event = {
        "status": "On Duty",
        "start": format_time(current_time),
        "end": format_time(current_time + timedelta(hours=1)),
        "description": "Pickup"
    }
    current_day_events.append(pickup_event)
    current_time += timedelta(hours=1)
    on_duty_hours += 1.0

    # --- Simulate Driving in 1-Hour Increments ---
    while remaining_driving > 0:
        # Determine maximum driving possible in the current day.
        available_driving = min(11 - driving_hours_today, 14 - on_duty_hours)
        # Drive in segments of 1 hour (or less if not enough time remains).
        drive_segment = min(1.0, remaining_driving, available_driving)
        if drive_segment <= 0:
            # End-of-day: add off-duty period (10 hours) and start next day.
            off_duty_duration = 10.0
            off_duty_event = {
                "status": "Off Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(hours=off_duty_duration)),
                "description": "Rest"
            }
            current_day_events.append(off_duty_event)
            daily_logs.append({
                "dayIndex": day_index,
                "events": current_day_events
            })
            day_index += 1
            # Reset for next day (start at 06:00 next day)
            current_day_events = []
            current_time = day_start + timedelta(days=day_index - 1)
            on_duty_hours = 0.0
            driving_hours_today = 0.0
            continue

        # Create a driving event.
        start_time = current_time
        end_time = current_time + timedelta(hours=drive_segment)
        driving_event = {
            "status": "Driving",
            "start": format_time(start_time),
            "end": format_time(end_time),
            "description": f"Driving segment for {drive_segment:.1f} hour(s)"
        }
        current_day_events.append(driving_event)
        driving_hours_today += drive_segment
        on_duty_hours += drive_segment
        remaining_driving -= drive_segment
        current_time = end_time

        # Update miles driven this segment.
        segment_miles = average_speed * drive_segment
        cumulative_miles += segment_miles

        # Insert fueling stop if cumulative miles cross threshold.
        if cumulative_miles >= next_fuel_mile:
            fuel_event = {
                "status": "On Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(minutes=15)),
                "description": "Fueling Stop"
            }
            current_day_events.append(fuel_event)
            fuel_stops.append({
                "mile": next_fuel_mile,
                "location": f"Fuel Stop at mile {next_fuel_mile}"
            })
            on_duty_hours += 0.25  # 15 minutes added as on-duty time
            current_time += timedelta(minutes=15)
            next_fuel_mile += 1000.0

        # After 8 hours of driving in a day, add a 30-minute break if there is still driving left.
        if driving_hours_today >= 8 and remaining_driving > 0:
            break_event = {
                "status": "On Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(minutes=30)),
                "description": "30-minute Break"
            }
            current_day_events.append(break_event)
            on_duty_hours += 0.5
            current_time += timedelta(minutes=30)

        # If daily limits are reached (11 hours driving or 14 hours on duty), end the day.
        if driving_hours_today >= 11 or on_duty_hours >= 14:
            off_duty_duration = 10.0
            off_duty_event = {
                "status": "Off Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(hours=off_duty_duration)),
                "description": "Rest, end of day"
            }
            current_day_events.append(off_duty_event)
            daily_logs.append({
                "dayIndex": day_index,
                "events": current_day_events
            })
            day_index += 1
            current_day_events = []
            current_time = day_start + timedelta(days=day_index - 1)
            on_duty_hours = 0.0
            driving_hours_today = 0.0

    # --- Add Dropoff Event on Final Day (1 hour) ---
    dropoff_event = {
        "status": "On Duty",
        "start": format_time(current_time),
        "end": format_time(current_time + timedelta(hours=1)),
        "description": "Dropoff"
    }
    current_day_events.append(dropoff_event)
    on_duty_hours += 1.0
    daily_logs.append({
        "dayIndex": day_index,
        "events": current_day_events
    })

    return route_coords, distance_miles, fuel_stops, daily_logs

class CalculateTripView(APIView):
    """
    API endpoint that accepts trip details,
    calculates route information and HOS-based daily logs,
    saves a Trip instance, and returns the stored data.
    """
    def post(self, request, format=None):
        data = request.data
        current_loc = data.get('currentLocation')
        pickup_loc = data.get('pickupLocation')
        dropoff_loc = data.get('dropoffLocation')
        try:
            cycle_used = float(data.get('currentCycleUsed', 0))
        except (ValueError, TypeError):
            cycle_used = 0.0

        # Use real API calls and HOS simulation.
        try:
            route, distance, fuel_stops, daily_logs = real_simulate_trip(
                current_loc, pickup_loc, dropoff_loc, cycle_used
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for saving
        trip_data = {
            "current_location": current_loc,
            "pickup_location": pickup_loc,
            "dropoff_location": dropoff_loc,
            "current_cycle_hours_used": cycle_used,
            "route": route,
            "logs": daily_logs,
            "distance": distance,
            "fuel_stops": fuel_stops,
        }

        serializer = TripSerializer(data=trip_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
