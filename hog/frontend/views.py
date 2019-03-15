from django.shortcuts import render

from api.models import Box


def box(request, code):
    box = Box.objects.get(code=code)
    context = {'box': box}
    return render(request, 'box.html', context=context)
