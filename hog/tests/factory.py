import random
import os

from django.conf import settings
from django.contrib.auth.models import User

from api.models import Hog
from api.models import Location
from api.models import Measurement


def dummy_video():
    path = os.path.join(settings.BASE_DIR, "media", "sample_file.mp4")
    return open(path, "rb")


def create_hog():
    counter = 0
    code = "hog-{}".format(counter)
    name = "Hog {}".format(counter)
    return Hog.objects.create(code=code, name=name)


def create_admin_user():
    return User.objects.create_superuser(
        "john", "lennon@thebeatles.com", "johnpassword"
    )


def create_location():
    counter = 0
    code = "loc-{}".format(counter)
    name = "Location {}".format(counter)
    location_type = random.choice(Location.LOCATION_TYPE_CHOICES)[0]
    return Location.objects.create(
        code=code, name=name, location_type=location_type, software_version="0.1"
    )
