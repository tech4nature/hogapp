"""hog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.conf.urls.static import static

from django_filters import FilterSet
from django_filters import ChoiceFilter

from api.models import Location
from api.models import Hog
from api.models import Measurement
from frontend.views import index
from frontend.views import location
from frontend.views import locations
from frontend.views import hog
from frontend.views import hogs

from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser

from rest_framework_swagger.views import get_swagger_view


class HogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hog
        fields = ('code', 'name')


class HogViewSet(viewsets.ModelViewSet):
    queryset = Hog.objects.all()
    serializer_class = HogSerializer


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('code', 'name', 'created_at', 'software_version')


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    hog_id = serializers.CharField(required=False)
    location_id = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that weight and video measurements always include a hog
        """
        if data['measurement_type'] in ['video', 'weight']:
            if 'hog_id' not in data:
                raise serializers.ValidationError("You must provide a hog_id")
        return data

    class Meta:
        model = Measurement
        fields = ('measurement_type', 'measurement',
                  'observed_at', 'video', 'hog_id', 'location_id')


class MeasurementFilter(FilterSet):

    resolution = ChoiceFilter(
        label='resolution',
        choices=(('hour', 'hour'), ('day', 'day')),
        method='noop'
    )

    class Meta:
        model = Measurement
        fields = ('location', 'hog', 'measurement_type',
                  'observed_at', 'resolution')

    def noop(self, queryset, name, value):
        return queryset


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    ordering_fields = ['observed_at', 'measurement_type']
    filterset_class = MeasurementFilter
    page_size_query_param = 'page_size'
    max_page_size = 10000
    parser_class = (FileUploadParser,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        resolution = request.query_params.get('resolution', None)
        measurement_type = request.query_params.get('measurement_type', None)
        if resolution:
            sql = open(os.path.join(
                settings.BASE_DIR,
                'api/sql/measurement_by_day.sql'), 'r').read()
            conditions = ['1 = 1']
            params = []
            location = request.query_params.get('location', None)
            if location:
                conditions.append("location_id = %s")
                params.append(location)
            hog = request.query_params.get('hog', None)
            if hog:
                conditions.append("hog_id = %s")
                params.append(hog)
            if measurement_type:
                conditions.append("measurement_type = %s")
                params.append(measurement_type)
            observed_at = request.query_params.get('observed_at', None)
            if observed_at:
                if resolution:
                    conditions.append("date_trunc(%s, observed_at) = %s")
                    params.append(resolution)
                else:
                    conditions.append("observed_at = %s")
                params.append(observed_at)
            conditions = " AND ".join(conditions)

            if resolution == 'day':
                date_type = 'date'
            else:
                date_type = 'timestamp'
            sql = sql.format(conditions=conditions, date_type=date_type)
            params = [resolution] + params + ['1 ' + resolution]
            params.append(hog)
            params.append(location)
            params.append(measurement_type)
            queryset = queryset.raw(
                sql, params)
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #    serializer = self.get_serializer(page, many=True)
        #    return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('hogs', HogViewSet)
router.register('locations', LocationViewSet)
router.register('measurements', MeasurementViewSet)


urlpatterns = [
    path('', index, name='index'),
    path('locations/', locations, name='locations'),
    path('hogs/', hogs, name='hogs'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('location/<slug:code>', location, name='location'),
    path('hog/<slug:code>', hog, name='hog'),
    path(r'docs/', get_swagger_view(title='Hog API')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
