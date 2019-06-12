from datetime import timedelta

from django.db.models import Max, Min
from django.shortcuts import render

from api.models import Hog
from api.models import Location
from api.models import Measurement


def index(request):
    return render(request, "index.html")


def locations(request):
    locations = Location.objects.all()
    context = {"locations": locations}
    return render(request, "locations.html", context=context)


def hogs(request):
    hogs = Hog.objects.all()
    context = {"hogs": hogs}
    return render(request, "hogs.html", context=context)


def location(request, code):
    location = Location.objects.get(code=code)
    measurements = Measurement.objects.filter(location=location)
    num_measurements = measurements.count()
    initial_resolution = "day"
    max_date = min_date = None
    if num_measurements:
        min_date = (
            measurements.aggregate(Min("observed_at"))["observed_at__min"].timestamp()
            * 1000
        )
        max_date = (
            measurements.aggregate(Max("observed_at"))["observed_at__max"].timestamp()
            * 1000
        )
        min_range = 3 * 24 * 60 * 60 * 1000
        if (max_date - min_date) < min_range:
            midpoint = min_date + (max_date - min_date) / 2
            min_date = midpoint - min_range / 2
            max_date = midpoint + min_range / 2
            initial_resolution = "hour"
    context = {
        "location": location,
        "min_date": min_date,
        "max_date": max_date,
        "num_measurements": num_measurements,
        "initial_resolution": initial_resolution,
    }
    return render(request, "location.html", context=context)


def location_temp_chart(request, code):
    location = Location.objects.get(code=code)
    measurements = Measurement.objects.filter(
        location=location, measurement_type__in=["in_temp", "out_temp"]
    )
    num_measurements = measurements.count()
    initial_resolution = "day"
    max_date = min_date = None
    if num_measurements:
        min_date = (
            measurements.aggregate(Min("observed_at"))["observed_at__min"].timestamp()
            * 1000
        )
        max_date = (
            measurements.aggregate(Max("observed_at"))["observed_at__max"].timestamp()
            * 1000
        )
        min_range = 3 * 24 * 60 * 60 * 1000
        if (max_date - min_date) < min_range:
            midpoint = min_date + (max_date - min_date) / 2
            min_date = midpoint - min_range / 2
            max_date = midpoint + min_range / 2
            initial_resolution = "hour"
    context = {
        "location": location,
        "min_date": min_date,
        "max_date": max_date,
        "num_measurements": num_measurements,
        "initial_resolution": initial_resolution,
    }
    return render(request, "location_temp_chart.html", context=context)


def hog_weight_chart(request, code):
    hog = Hog.objects.get(code=code)
    measurements = Measurement.objects.filter(hog=hog, measurement_type="weight")
    num_measurements = measurements.count()
    initial_resolution = "day"
    max_date = min_date = None
    if num_measurements:
        min_date = (
            measurements.aggregate(Min("observed_at"))["observed_at__min"].timestamp()
            * 1000
        )
        max_date = (
            measurements.aggregate(Max("observed_at"))["observed_at__max"].timestamp()
            * 1000
        )
        min_range = 3 * 24 * 60 * 60 * 1000
        if (max_date - min_date) < min_range:
            midpoint = min_date + (max_date - min_date) / 2
            min_date = midpoint - min_range / 2
            max_date = midpoint + min_range / 2
            initial_resolution = "hour"
    context = {
        "hog": hog,
        "min_date": min_date,
        "max_date": max_date,
        "num_measurements": num_measurements,
        "initial_resolution": initial_resolution,
    }
    return render(request, "hog_weight_chart.html", context=context)


def _add_location_measurement_to_group(group, group_duration):
    first_in_group = list(group.values())[0]
    location = first_in_group.location
    location_measurements = location.measurement_set.filter(
        hog=None,
        observed_at__gte=first_in_group.observed_at,
        observed_at__lte=first_in_group.observed_at + timedelta(seconds=group_duration),
    )
    for measurement in location_measurements:
        if measurement.measurement_type not in group:
            print(group)
            group[measurement.measurement_type] = measurement
    return group


def grouped_measurements(hog=None, group_duration=600):
    """Return an array of groups of measurements that happened within a
    `group_duration` seconds of each other

    """
    measurements = (
        Measurement.objects.filter(hog=hog)
        .exclude(video="", measurement_type="video")
        .reverse()
    )
    groups = []

    current_group = {}

    current_group_start = None
    # XXX we should average measurements within group
    for measurement in measurements:
        if current_group_start is None:
            current_group_start = measurement.observed_at
            current_group["header"] = measurement
        if (current_group_start - measurement.observed_at).seconds < group_duration:
            current_group[measurement.measurement_type] = measurement
        else:
            current_group = _add_location_measurement_to_group(
                current_group, group_duration
            )
            groups.append(current_group)
            current_group = {}
            current_group["header"] = measurement
            current_group[measurement.measurement_type] = measurement
            current_group_start = measurement.observed_at
    if current_group:
        current_group = _add_location_measurement_to_group(
            current_group, group_duration
        )
        groups.append(current_group)
    return groups


def hog(request, code):
    hog = Hog.objects.get(code=code)
    measurements = grouped_measurements(hog)
    context = {"hog": hog, "grouped_measurements": measurements}
    return render(request, "hog.html", context=context)
