import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TripSerializer
from .models import Trip, Driver

load_dotenv()

# OpenRouteService (ORS) API key
ORS_API_KEY = os.environ.get("ORS_API_KEY")
if not ORS_API_KEY:
    raise Exception("ORS_API_KEY not set in environment variables.")

# Constants for HOS rules and cycle limits
MAX_CYCLE_HOURS = 70.0        # Maximum allowed cycle hours per cycle
PICKUP_DURATION = 1.0         # 1-hour pickup event
DROPOFF_DURATION = 1.0        # 1-hour dropoff event
DRIVING_LIMIT = 11.0          # Maximum 11 hours driving per day
ONDUTY_LIMIT = 14.0           # Maximum 14 hours on-duty per day
BREAK_AFTER_DRIVING = 8.0     # 30-minute break after 8 hours driving
BREAK_DURATION = 0.5          # 0.5 hours (30 minutes)
REST_DURATION = 10.0          # 10-hour mandatory off-duty rest
FUEL_MILE_INTERVAL = 1000.0   # Fueling stop every 1000 miles
AVERAGE_SPEED = 50.0          # Average speed in mph

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
            return data["features"][0]["geometry"]["coordinates"]
    raise Exception(f"Geocoding failed for address: {address}")

def get_directions(route_coords):
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
    return dir_resp.json()

def real_simulate_trip(current_loc, pickup_loc, dropoff_loc, cycle_used):
    # --- Step 1: Geocode Addresses ---
    current_coords = geocode_address(current_loc)
    pickup_coords = geocode_address(pickup_loc)
    dropoff_coords = geocode_address(dropoff_loc)
    route_coords = [current_coords, pickup_coords, dropoff_coords]

    # --- Step 2: Get Directions and Calculate Distance ---
    directions_data = get_directions(route_coords)
    summary = directions_data["routes"][0]["summary"]
    distance_meters = summary["distance"]
    distance_miles = distance_meters / 1609.34
    distance_miles = round(distance_miles, 2)
    total_driving_hours = distance_miles / AVERAGE_SPEED

    # --- Step 3: Initialize Simulation Variables ---
    def format_time(time_obj):
        return time_obj.strftime("%H:%M")

    daily_logs = []
    day_index = 1
    current_day_events = []
    day_start = datetime.strptime("06:00", "%H:%M")
    current_time = day_start
    on_duty_hours = 0.0
    driving_hours_today = 0.0
    remaining_driving = total_driving_hours
    remaining_cycle_hours = MAX_CYCLE_HOURS - cycle_used
    cumulative_miles = 0.0
    next_fuel_mile = FUEL_MILE_INTERVAL
    fuel_stops = []

    # --- Add Pickup Event (1 hour) ---
    pickup_event = {
        "status": "On Duty",
        "start": format_time(current_time),
        "end": format_time(current_time + timedelta(hours=PICKUP_DURATION)),
        "description": "Pickup"
    }
    current_day_events.append(pickup_event)
    current_time += timedelta(hours=PICKUP_DURATION)
    on_duty_hours += PICKUP_DURATION

    # --- Simulate Driving with HOS and Cycle Limit Integration ---
    while remaining_driving > 0:
        daily_available = min(DRIVING_LIMIT - driving_hours_today, ONDUTY_LIMIT - on_duty_hours)
        available_cycle_hours = remaining_cycle_hours - on_duty_hours

        if available_cycle_hours <= 0 or daily_available <= 0:
            cycle_event = {
                "status": "Cycle Limit Reached",
                "start": format_time(current_time),
                "end": format_time(current_time),
                "description": "Driver has reached the maximum cycle hours."
            }
            current_day_events.append(cycle_event)
            daily_logs.append({
                "dayIndex": day_index,
                "events": current_day_events
            })
            break

        drive_segment = min(1.0, remaining_driving, daily_available, available_cycle_hours)
        if drive_segment <= 0:
            off_duty_event = {
                "status": "Off Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(hours=REST_DURATION)),
                "description": "End of day rest"
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
            continue

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

        segment_miles = AVERAGE_SPEED * drive_segment
        cumulative_miles += segment_miles

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
            on_duty_hours += 0.25
            current_time += timedelta(minutes=15)
            next_fuel_mile += FUEL_MILE_INTERVAL

        if driving_hours_today >= BREAK_AFTER_DRIVING and remaining_driving > 0:
            break_event = {
                "status": "On Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(minutes=30)),
                "description": "30-minute Break"
            }
            current_day_events.append(break_event)
            on_duty_hours += BREAK_DURATION
            current_time += timedelta(minutes=30)

        if driving_hours_today >= DRIVING_LIMIT or on_duty_hours >= ONDUTY_LIMIT:
            off_duty_event = {
                "status": "Off Duty",
                "start": format_time(current_time),
                "end": format_time(current_time + timedelta(hours=REST_DURATION)),
                "description": "End of day rest"
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

    if remaining_driving <= 0:
        dropoff_event = {
            "status": "On Duty",
            "start": format_time(current_time),
            "end": format_time(current_time + timedelta(hours=DROPOFF_DURATION)),
            "description": "Dropoff"
        }
        current_day_events.append(dropoff_event)
        on_duty_hours += DROPOFF_DURATION
        daily_logs.append({
            "dayIndex": day_index,
            "events": current_day_events
        })

    return route_coords, distance_miles, fuel_stops, daily_logs

def build_eld_log_form(daily_logs):
    SLOTS_PER_DAY = 96
    MINUTES_PER_SLOT = 15

    def time_to_slot(t_str):
        hh, mm = map(int, t_str.split(":"))
        total_minutes = hh * 60 + mm
        slot_index = total_minutes // MINUTES_PER_SLOT
        return max(0, min(slot_index, SLOTS_PER_DAY - 1))

    DEFAULT_STATUS = "Off Duty"

    form_data = []
    for day_log in daily_logs:
        day_index = day_log["dayIndex"]
        events = day_log["events"]
        day_timeline = [DEFAULT_STATUS for _ in range(SLOTS_PER_DAY)]
        for event in events:
            status = event["status"]
            start_slot = time_to_slot(event["start"])
            end_slot = time_to_slot(event["end"])
            if end_slot <= start_slot:
                end_slot = start_slot + 1
            for slot_idx in range(start_slot, min(end_slot, SLOTS_PER_DAY)):
                day_timeline[slot_idx] = status
        form_data.append({
            "dayIndex": day_index,
            "timeline": day_timeline
        })
    return form_data

class CalculateTripView(APIView):
    def post(self, request, format=None):
        data = request.data
        current_loc = data.get('currentLocation')
        pickup_loc = data.get('pickupLocation')
        dropoff_loc = data.get('dropoffLocation')
        
        # Retrieve driver using driverId (if provided) or create a new driver with driverName.
        driver_id = data.get('driverId', '').strip()
        driver_name = data.get('driverName', '').strip()

        if driver_id:
            try:
                driver = Driver.objects.get(id=driver_id)
            except Driver.DoesNotExist:
                return Response({"error": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            if not driver_name:
                return Response({"error": "Driver name is required if no driver ID is provided."}, status=status.HTTP_400_BAD_REQUEST)
            driver = Driver.objects.create(name=driver_name)
        
        # Use the driver's current cycle hours as the starting point.
        try:
            cycle_used = float(driver.current_cycle_hours_used)
        except (ValueError, TypeError):
            cycle_used = 0.0

        try:
            route, distance, fuel_stops, daily_logs = real_simulate_trip(
                current_loc, pickup_loc, dropoff_loc, cycle_used
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        eld_form_data = build_eld_log_form(daily_logs)
        
        # Calculate the on-duty hours consumed during this trip.
        trip_cycle_hours_used = sum(
            1.0 for day in daily_logs for event in day.get("events", [])
            if event["status"] != "Off Duty"
        )
        # Update the driver's cumulative cycle hours.
        driver.current_cycle_hours_used += trip_cycle_hours_used
        driver.save()

        trip_data = {
            "driver": driver.id,
            "current_location": current_loc,
            "pickup_location": pickup_loc,
            "dropoff_location": dropoff_loc,
            "cycle_hours_used": trip_cycle_hours_used,
            "route": route,
            "logs": daily_logs,
            "distance": distance,
            "fuel_stops": fuel_stops,
            "eldFormData": eld_form_data,
        }

        serializer = TripSerializer(data=trip_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
