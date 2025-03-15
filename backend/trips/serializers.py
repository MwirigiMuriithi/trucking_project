from rest_framework import serializers
from .models import Trip

class TripSerializer(serializers.ModelSerializer):
    eldFormData = serializers.JSONField(read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id',
            'current_location',
            'pickup_location',
            'dropoff_location',
            'current_cycle_hours_used',
            'route',
            'logs',
            'distance',
            'fuel_stops',
            'eldFormData'
        ]

