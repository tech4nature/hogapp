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
from django_filters.rest_framework import DjangoFilterBackend

from api.models import Location
from api.models import Hog
from api.models import Measurement
from frontend.views import index
from frontend.views import location
from frontend.views import location_temp_chart
from frontend.views import hog_weight_chart
from frontend.views import locations
from frontend.views import hog
from frontend.views import hogs
from frontend.views import measurement
from frontend.views import card_wall_fragment

from rest_framework import routers, serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser

from rest_framework_swagger.views import get_swagger_view


class HogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hog
        fields = ("code", "name")


class HogViewSet(viewsets.ModelViewSet):
    queryset = Hog.objects.all()
    serializer_class = HogSerializer


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ("code", "name", "created_at", "software_version", "coords")


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("code",)


class MeasurementSerializer(serializers.ModelSerializer):
    hog_id = serializers.CharField(required=False)
    location_id = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that weight measurements always include a hog
        """
        if data["measurement_type"] in ["weight"]:
            if "hog_id" not in data:
                raise serializers.ValidationError("You must provide a hog_id")
        return data

    class Meta:
        model = Measurement
        fields = (
            "id",
            "measurement_type",
            "measurement",
            "observed_at",
            "video",
            "hog_id",
            "location_id",
        )
        read_only_fields = ("video",)


class MeasurementVideoSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        """Rename the filename to match the measurement id
        """
        validated_data["video"].name = "{}.mp4".format(instance.pk)
        return super().update(instance, validated_data)

    class Meta:
        model = Measurement
        fields = ["video"]


class MeasurementFilter(FilterSet):

    resolution = ChoiceFilter(
        label="resolution", choices=(("hour", "hour"), ("day", "day")), method="noop"
    )

    class Meta:
        model = Measurement
        fields = ("location", "hog", "measurement_type", "observed_at", "resolution")

    def noop(self, queryset, name, value):
        return queryset


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    ordering_fields = ["observed_at", "measurement_type"]
    filterset_class = MeasurementFilter
    page_size_query_param = "page_size"
    max_page_size = 10000

    @action(
        detail=True,
        methods=["PUT"],
        serializer_class=MeasurementVideoSerializer,
        parser_classes=[MultiPartParser],
    )
    def video(self, request, pk):
        from utils import delayed_make_poster

        obj = self.get_object()
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if obj.measurement_type == "video":
                delayed_make_poster(obj)

            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """A custom `list` action that optionally aggregates measurements to
        hours or days

        """
        queryset = self.filter_queryset(self.get_queryset())
        resolution = request.query_params.get("resolution", None)
        measurement_type = request.query_params.get("measurement_type", None)
        if resolution:
            sql = open(
                os.path.join(settings.BASE_DIR, "api/sql/measurement_by_day.sql"), "r"
            ).read()
            conditions = ["1 = 1"]
            params = []
            location = request.query_params.get("location", None)
            if location:
                conditions.append("location_id = %s")
                params.append(location)
            hog = request.query_params.get("hog", None)
            if hog:
                conditions.append("hog_id = %s")
                params.append(hog)
            if measurement_type:
                conditions.append("measurement_type = %s")
                params.append(measurement_type)
            observed_at = request.query_params.get("observed_at", None)
            if observed_at:
                if resolution:
                    conditions.append("date_trunc(%s, observed_at) = %s")
                    params.append(resolution)
                else:
                    conditions.append("observed_at = %s")
                params.append(observed_at)
            conditions = " AND ".join(conditions)

            if resolution == "day":
                date_type = "date"
            else:
                date_type = "timestamp"
            sql = sql.format(conditions=conditions, date_type=date_type)
            params = [resolution] + params + ["1 " + resolution]
            params.append(hog)
            params.append(location)
            params.append(measurement_type)
            queryset = queryset.raw(sql, params)
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #    serializer = self.get_serializer(page, many=True)
        #    return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register("hogs", HogViewSet)
router.register("locations", LocationViewSet)
router.register("measurements", MeasurementViewSet)


urlpatterns = [
    path("", index, name="index"),
    path("locations/", locations, name="locations"),
    path("hogs/", hogs, name="hogs"),
    path("measurement/<slug:measurement_id>", measurement, name="measurement"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("location/<slug:code>", location, name="location"),
    path(
        "location/<slug:code>/temp_chart",
        location_temp_chart,
        name="location_temp_chart",
    ),
    path("hog/<slug:code>", hog, name="hog"),
    path("card_wall_fragment", card_wall_fragment, name="card_wall_fragment"),
    path("hog/<slug:code>/weight_chart", hog_weight_chart, name="hog_weight_chart"),
    path(r"docs/", get_swagger_view(title="Hog API")),
]
