from django.contrib import admin
from django.urls import path
from trips.views import CalculateTripView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/calculate-trip/', CalculateTripView.as_view(), name='calculate_trip'),
]
