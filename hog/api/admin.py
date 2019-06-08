from django.contrib import admin

from .models import Location
from .models import Measurement
from .models import Hog


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("observed_at", "measurement_type", "measurement", "location", "hog")
    list_filter = ("measurement_type", "observed_at", "hog", "location")


admin.site.register(Location)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(Hog)
