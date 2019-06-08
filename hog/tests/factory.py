import random

from api.models import Hog
from api.models import Location
from api.models import Measurement


def create_hog():
    counter = 0
    code = "hog-{}".format(counter)
    name = "Hog {}".format(counter)
    return Hog.objects.create(code=code, name=name)


def create_location():
    counter = 0
    code = "loc-{}".format(counter)
    name = "Location {}".format(counter)
    location_type = random.choice(Location.LOCATION_TYPE_CHOICES)[0]
    return Location.objects.create(
        code=code, name=name, location_type=location_type, software_version="0.1"
    )
