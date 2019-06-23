from django.contrib import admin
from django.contrib.gis.db import models

from mapwidgets.widgets import GooglePointFieldWidget

from .models import Location
from .models import Measurement
from .models import Hog


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("observed_at", "measurement_type", "measurement", "location", "hog")
    list_filter = ("measurement_type", "observed_at", "hog", "location", "starred")


class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {models.PointField: {"widget": GooglePointFieldWidget}}


admin.site.register(Location, LocationAdmin)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(Hog)
