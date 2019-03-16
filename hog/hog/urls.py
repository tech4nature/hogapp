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
from django.contrib import admin
from django.urls import include
from django.urls import path

from django_filters import FilterSet

from api.models import Box
from api.models import Hog
from api.models import Measurement
from frontend.views import box

from rest_framework import routers, serializers, viewsets


class HogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hog
        fields = ('code', 'name')


class HogViewSet(viewsets.ModelViewSet):
    queryset = Hog.objects.all()
    serializer_class = HogSerializer


class BoxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Box
        fields = ('code', 'name', 'created_at', 'software_version')


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measurement
        fields = ('measurement_type', 'measurement', 'observed_at')


class MeasurementFilter(FilterSet):
    class Meta:
        model = Measurement
        fields = ('box', 'hog', 'measurement_type', 'observed_at')


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    ordering_fields = ['observed_at', 'measurement_type']
    filterset_class = MeasurementFilter
    page_size_query_param = 'page_size'
    max_page_size = 10000


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('hogs', HogViewSet)
router.register('boxes', BoxViewSet)
router.register('measurements', MeasurementViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('box/<slug:code>', box),
]
