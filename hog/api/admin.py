from django.contrib.gis.db import models
from django.contrib.gis import admin
from django.contrib.gis.geos import Point

from mapwidgets.widgets import GooglePointFieldWidget

from .models import Location
from .models import Measurement
from .models import Hog
from .models import Republic


def convert_lon_lat(lon, lat):
    # OSMGeoAdmin and its base class use different SRIDs...
    # https://code.djangoproject.com/ticket/11094#comment:4
    pnt = Point(lon, lat, srid=4326)
    pnt.transform(3857)
    return pnt.coords


class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("observed_at", "measurement_type", "measurement", "location", "hog")
    list_filter = ("measurement_type", "observed_at", "hog", "location", "starred")


class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {models.PointField: {"widget": GooglePointFieldWidget}}


class RepublicAdmin(admin.OSMGeoAdmin):
    default_lon, default_lat = convert_lon_lat(-2.21541, 51.74051)
    default_zoom = 14


admin.site.register(Location, LocationAdmin)
admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(Hog)
admin.site.register(Republic, RepublicAdmin)
