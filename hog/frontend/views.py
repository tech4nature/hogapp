from django.db.models import Max, Min
from django.shortcuts import render

from api.models import Hog
from api.models import Location
from api.models import Measurement


def index(request):
    return render(request, 'index.html')


def locations(request):
    locations = Location.objects.all()
    context = {'locations': locations}
    return render(request, 'locations.html', context=context)


def hogs(request):
    hogs = Hog.objects.all()
    context = {'hogs': hogs}
    return render(request, 'hogs.html', context=context)


def location(request, code):
    location = Location.objects.get(code=code)
    measurements = Measurement.objects.filter(location=location)
    num_measurements = measurements.count()
    initial_resolution = 'day'
    max_date = min_date = None
    if num_measurements:
        min_date = measurements.aggregate(
            Min('observed_at'))['observed_at__min'].timestamp() * 1000
        max_date = measurements.aggregate(
            Max('observed_at'))['observed_at__max'].timestamp() * 1000
        min_range = 3 * 24 * 60 * 60 * 1000
        if (max_date - min_date) < min_range:
            midpoint = min_date + (max_date - min_date)/2
            min_date = midpoint - min_range / 2
            max_date = midpoint + min_range / 2
            initial_resolution = 'hour'
    context = {'location': location,
               'min_date': min_date,
               'max_date': max_date,
               'num_measurements': num_measurements,
               'initial_resolution': initial_resolution}
    return render(request, 'location.html', context=context)


def hog(request, code):
    hog = Hog.objects.get(code=code)
    videos = Measurement.objects.filter(measurement_type='video', hog=hog)
    context = {'hog': hog, 'video_measurements': videos}
    return render(request, 'hog.html', context=context)
