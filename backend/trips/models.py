from django.db import models

class Trip(models.Model):
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours_used = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    route = models.JSONField(blank=True, null=True)
    logs = models.JSONField(blank=True, null=True)
    distance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    fuel_stops = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Trip {self.id}: {self.pickup_location} to {self.dropoff_location}"
