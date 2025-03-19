# from django.db import models

# class Trip(models.Model):
#     current_location = models.CharField(max_length=255)
#     pickup_location = models.CharField(max_length=255)
#     dropoff_location = models.CharField(max_length=255)
#     current_cycle_hours_used = models.DecimalField(max_digits=4, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     route = models.JSONField(blank=True, null=True)
#     logs = models.JSONField(blank=True, null=True)
#     distance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
#     fuel_stops = models.JSONField(blank=True, null=True)

#     def __str__(self):
#         return f"Trip {self.id}: {self.pickup_location} to {self.dropoff_location}"


from django.db import models

class Driver(models.Model):
    name = models.CharField(max_length=255)
    # Cumulative cycle hours used during the current 70-hour cycle.
    current_cycle_hours_used = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    # When the current cycle started; helps determine the 8-day period.
    cycle_start_date = models.DateField(auto_now_add=True)
    # Optionally store aggregated weekly (70hr/8-day) logs.
    weekly_logs = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

class Trip(models.Model):
    # Each trip is linked to a driver.
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="trips")
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    # This field captures the on-duty hours consumed during the trip.
    cycle_hours_used = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    route = models.JSONField(blank=True, null=True)
    logs = models.JSONField(blank=True, null=True)
    distance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    fuel_stops = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Trip {self.id}: {self.pickup_location} to {self.dropoff_location}"

