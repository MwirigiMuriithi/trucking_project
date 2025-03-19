# from rest_framework import serializers
# from .models import Trip

# class TripSerializer(serializers.ModelSerializer):
#     eldFormData = serializers.JSONField(read_only=True)
    
#     class Meta:
#         model = Trip
#         fields = [
#             'id',
#             'current_location',
#             'pickup_location',
#             'dropoff_location',
#             'current_cycle_hours_used',
#             'route',
#             'logs',
#             'distance',
#             'fuel_stops',
#             'eldFormData'
#         ]


from rest_framework import serializers
from .models import Trip, Driver

class TripSerializer(serializers.ModelSerializer):
    # eldFormData is computed from the logs on the backend.
    eldFormData = serializers.JSONField(read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id',
            'driver',
            'current_location',
            'pickup_location',
            'dropoff_location',
            'cycle_hours_used',
            'route',
            'logs',
            'distance',
            'fuel_stops',
            'eldFormData'
        ]

