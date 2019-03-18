from django.db.models import Max, Min
from django.shortcuts import render

from api.models import Location
from api.models import Measurement


def index(request):
    locations = Location.objects.all()
    context = {'locations': locations}
    return render(request, 'index.html', context=context)


def location(request, code):
    location = Location.objects.get(code=code)
    measurements = Measurement.objects.filter(location=location)
    min_date = measurements.aggregate(Min('observed_at'))['observed_at__min'].timestamp() * 1000
    max_date = measurements.aggregate(Max('observed_at'))['observed_at__max'].timestamp() * 1000
    context = {'location': location,
               'min_date': min_date,
               'max_date': max_date}
    return render(request, 'location.html', context=context)
