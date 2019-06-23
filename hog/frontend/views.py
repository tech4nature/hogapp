from datetime import timedelta

from django.db.models import Max, Min
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string

from api.models import Hog
from api.models import Location
from api.models import Measurement


def index(request):
    videos = (
        Measurement.objects.filter(measurement_type="video")
        .order_by("-starred", "-observed_at")
        .exclude(video="")[:2]
    )
    grouped = [
        {"header": x, x.measurement_type: x, "video": x, x.measurement_type: x}
        for x in videos
    ]
    return render(request, "index.html", context={"videos": grouped})


def locations(request):
    locations = Location.objects.all()
    context = {"locations": locations}
    return render(request, "locations.html", context=context)


def hogs(request):
    hogs = Hog.objects.all()
    context = {"hogs": hogs}
    return render(request, "hogs.html", context=context)


def location(request, code):
    location = get_object_or_404(Location, code=code)
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
    location = get_object_or_404(Location, code=code)
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
    hog = get_object_or_404(Hog, code=code)
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


def _finalise_group(group, group_duration, add_location_only_measurements=False):
    """Record the final measurement seen in the header, to support paging
    through cards.

    For groups that are hog-focussed, add location-only measurements,
    so that the card lists hog activity *and* things that happened in
    that location in one place.

    """
    # Record the last measurement id in the header, so we can page
    # through them
    measurements = list(group.values())
    first_in_group = measurements[0]
    last_in_group = measurements[-1]
    group["header"].last_id = last_in_group.id

    if add_location_only_measurements:
        location = first_in_group.location
        location_measurements = location.measurement_set.filter(
            hog=None,
            observed_at__gte=first_in_group.observed_at,
            observed_at__lte=first_in_group.observed_at
            + timedelta(seconds=group_duration),
        )
        for measurement in location_measurements:
            if measurement.measurement_type not in group:
                group[measurement.measurement_type] = measurement
    return group


def grouped_measurements(
    hog=None, location=None, group_duration=3600, max_cards=20, most_recent_id=None
):
    """Return an array of groups of measurements that happened within a
    `group_duration` seconds of each other; split measurements of
    different hogs into different groups.

    """
    kwargs = {}
    if hog:
        kwargs["hog"] = hog
    if location:
        kwargs["location"] = location
    if most_recent_id:
        kwargs["id__lt"] = most_recent_id
    max_measurements_per_card = 3  # this is a typical maximum, not including outliers
    limit = max_cards * max_measurements_per_card
    measurements = (
        Measurement.objects.filter(**kwargs)
        .exclude(video="", measurement_type="video")
        .order_by("-starred", "-id")[:limit]
    )
    groups = []
    current_group = {}

    current_group_start = None
    last_measurement = None
    cards = 0
    no_location = not location
    # XXX we should average measurements within group
    for measurement in measurements:
        if current_group_start is None:
            # Start the first card in the pack
            current_group_start = measurement.observed_at
            current_group["header"] = measurement
            last_measurement = measurement
        if (
            (
                measurement.measurement_type.endswith("temp")
                and last_measurement.measurement_type.endswith("temp")
            )
            or measurement.hog == last_measurement.hog
            and (
                (current_group_start - measurement.observed_at).seconds < group_duration
            )
        ):
            # It's still the same hog and we're within the same time
            # window; or it's a string of temperatures
            current_group[measurement.measurement_type] = measurement
        else:
            current_group = _finalise_group(
                current_group,
                group_duration,
                add_location_only_measurements=no_location,
            )
            if len(current_group) > 1:
                # when length is 1, the current group is only a
                # header. This is an edge case in the first iteration
                # of the loop, where group_dureation is zero
                groups.append(current_group)
                cards += 1
            current_group = {}
            current_group["header"] = measurement
            current_group[measurement.measurement_type] = measurement
            current_group_start = measurement.observed_at
            if cards == (max_cards - 1):
                break
        last_measurement = measurement
    if current_group:
        current_group = _finalise_group(
            current_group, group_duration, add_location_only_measurements=no_location
        )

        groups.append(current_group)
    return groups


def card_wall_fragment(request):
    """Just the HTML for the wall, suitable for inclusion within a full HTML page
    """
    max_cards = int(request.GET.get("max_cards", 6))
    most_recent_id = request.GET.get("most_recent_id")
    location = request.GET.get("location")
    hog = request.GET.get("hog")
    measurements = grouped_measurements(
        hog=hog, max_cards=max_cards, location=location, most_recent_id=most_recent_id
    )
    if measurements:
        last_id = measurements[-1]["header"].last_id
    else:
        last_id = ""
    return render(
        request,
        "_card_wall.html",
        context={"grouped_measurements": measurements, "last_id": last_id},
    )


def hog(request, code):
    hog = get_object_or_404(Hog, code=code)
    max_date = (
        hog.measurement_set.order_by("observed_at").last().observed_at.timestamp()
    )
    min_date = (
        hog.measurement_set.order_by("observed_at").first().observed_at.timestamp()
    )
    context = {
        "hog": hog,
        "min_date": min_date,
        "max_date": max_date,
        "initial_resolution": "day",
    }
    return render(request, "hog.html", context=context)


def measurement(request, measurement_id):
    measurement = get_object_or_404(Measurement, pk=measurement_id)
    group = {"header": measurement, measurement.measurement_type: measurement}
    if measurement.hog:
        title = "{} at {}".format(measurement.hog, measurement.location)
    else:
        if measurement.measurement_type == "video":
            title = "Video at {}".format(measurement.location)
        else:
            title = "Measurement at {}".format(measurement.location)
    if measurement.video_poster:
        image = measurement.video_poster.url
    elif measurement.hog and measurement.hog.avatar:
        image = measurement.hog.avatar.url
    else:
        image = None
    title += " in the Hedgehog Republic, {}".format(
        measurement.observed_at.strftime("%d/%m/%Y")
    )
    if measurement.measurement_type == "video":
        og_type = "video.other"
    else:
        og_type = "website"

    context = {"group": group, "title": title, "image": image, "og_type": og_type}

    return render(request, "measurement.html", context=context)
