from django.shortcuts import render

from api.models import Location


def index(request):
    locations = Location.objects.all()
    context = {'locations': locations}
    return render(request, 'index.html', context=context)


def location(request, code):
    location = Location.objects.get(code=code)
    context = {'location': location}
    return render(request, 'location.html', context=context)
