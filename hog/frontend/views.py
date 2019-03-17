from django.shortcuts import render

from api.models import Location


def location(request, code):
    locationur = Location.objects.get(code=code)
    context = {'location': location}
    return render(request, 'location.html', context=context)
