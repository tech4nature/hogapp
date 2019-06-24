"""Generate some sample data to play with
"""

from datetime import datetime
from datetime import timedelta
import logging
import random
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.files import File
from django.conf import settings
from django.contrib.gis.geos import Point

from api.models import Location
from api.models import Hog
from api.models import Measurement

from faker.providers import BaseProvider
from faker import Faker
import numpy as np
import pytz


def make_faker():
    fake = Faker()

    class Provider(BaseProvider):
        days = 365
        x = np.arange(days)
        TEMPS = (np.sin(2 * np.pi * (x / days)) + 1) * 13

        def temperature(self, date_time):
            day_of_year = date_time.timetuple().tm_yday
            # shift sine wave 0.25 to R to make peak in middle of year
            day_of_year = (day_of_year + 365 * 0.75) % 365
            baseline = Provider.TEMPS[int(day_of_year) - 1]
            jitter = random.choice(range(-30, 30)) / 10
            return baseline + jitter

        def weight(self, date_time):
            month = date_time.month
            month_baselines = [
                300,
                300,
                300,
                340,
                450,
                500,
                510,
                500,
                450,
                400,
                350,
                300,
            ]
            baseline = month_baselines[month - 1] * 10
            return random.choice(range(baseline, baseline + 50)) / 10.0

    fake.add_provider(Provider)
    return fake


NUM_BOXES = 2
NUM_HOGS = 2


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = make_faker()
        start_date = datetime(2018, 10, 1, 1, tzinfo=pytz.utc)
        end_date = datetime(2019, 4, 1, 1, tzinfo=pytz.utc)
        with transaction.atomic():
            Measurement.objects.all().delete()
            Location.objects.all().delete()
            Hog.objects.all().delete()
            observed_at = start_date
            boxes = []
            for box in range(0, NUM_BOXES):
                print("box {}".format(box))
                box1, _ = Location.objects.get_or_create(
                    code="box-" + fake.ean13(),
                    location_type="box",
                    name=fake.company() + " Box",
                    software_version="0.6",
                    coords=Point(
                        float(fake.coordinate(center=-2.207, radius=0.008)),
                        float(fake.coordinate(center=51.74220, radius=0.002)),
                    ),
                )
                boxes.append(box1)
            hogs = []
            for i in range(0, NUM_HOGS):
                hog, _ = Hog.objects.get_or_create(code="hog-{}".format(i), name=str(i))
                hogs.append(hog)

            while observed_at < end_date:
                print("  measurement {}".format(_))
                box1 = random.choice(boxes)
                observed_at += timedelta(seconds=random.choice(range(0, 60 * 60 * 24)))
                out_temp = fake.temperature(observed_at)
                Measurement.objects.create(
                    location=box1,
                    measurement_type="out_temp",
                    measurement=out_temp,
                    observed_at=observed_at,
                )
                in_temp = (out_temp * 10 + random.choice(range(0, 30))) / 10.0
                Measurement.objects.create(
                    location=box1,
                    measurement_type="in_temp",
                    measurement=in_temp,
                    observed_at=observed_at + timedelta(milliseconds=500),
                )

                hog = random.choice(hogs)
                print("  hog {}".format(hog))
                should_visit = random.choice([0, 1, 2]) == 1
                time_jitter = random.choice(range(60, 60 * 60 * 2))
                if should_visit:
                    print("   uploading a vid")
                    vid = random.choice(
                        ["hog2.mp4", "hog3.mp4", "hog4.mp4", "hog5.mp4"]
                    )
                    with open(os.path.join(settings.MEDIA_ROOT, vid), "rb") as f:
                        fake_video = File(f)
                        # A random number of visits where each hog gets weighed
                        weight = fake.weight(observed_at)
                        Measurement.objects.create(
                            hog=hog,
                            location=box1,
                            measurement_type="weight",
                            measurement=weight,
                            observed_at=observed_at + timedelta(seconds=time_jitter),
                        )
                        m = Measurement.objects.create(
                            hog=hog,
                            location=box1,
                            measurement_type="video",
                            observed_at=observed_at + timedelta(seconds=time_jitter),
                        )
                        m.video.save("sample_video.mp4", fake_video)
