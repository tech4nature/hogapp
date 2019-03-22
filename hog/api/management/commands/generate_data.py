"""Generate some sample data to play with
"""

from datetime import datetime
from datetime import timedelta
import logging
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Location
from api.models import Hog
from api.models import Measurement

from faker.providers import BaseProvider
from faker import Faker
import pytz


def make_faker():
    fake = Faker()

    class Provider(BaseProvider):
        def temperature(self, date_time):
            month = date_time.month
            month_baselines = [3, 6, 8, 10, 18, 20,
                               20, 18, 14, 10, 6, 4]
            baseline = month_baselines[month-1] * 10
            return random.choice(
                range(
                    baseline, baseline + 5)) / 10.0

        def weight(self, date_time):
            month = date_time.month
            month_baselines = [300, 300, 300, 340, 450, 500,
                               510, 500, 450, 400, 350, 300]
            baseline = month_baselines[month-1] * 10
            return random.choice(
                range(
                    baseline, baseline + 50)) / 10.0

    fake.add_provider(Provider)
    return fake


NUM_BOXES = 5
NUM_HOGS_PER_BOX = 3


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = make_faker()
        start_date = datetime(2018, 10, 1, 1, tzinfo=pytz.utc)
        end_date = datetime(2019, 4, 1, 1, tzinfo=pytz.utc)
        seconds = list(
            range(0,
                  int((end_date - start_date).total_seconds())))
        with transaction.atomic():
            Measurement.objects.all().delete()
            Location.objects.all().delete()
            Hog.objects.all().delete()
            for box in range(0, NUM_BOXES):
                box1, _ = Location.objects.get_or_create(
                    code='box-' + fake.ean13(),
                    location_type='box',
                    name=fake.company() + " Box",
                    software_version='0.6')
                for _ in range(0, 1800):
                    observed_at = start_date + timedelta(
                        seconds=random.choice(seconds))
                    out_temp = fake.temperature(observed_at)
                    Measurement.objects.create(
                        location=box1,
                        measurement_type='out_temp',
                        measurement=out_temp,
                        observed_at=observed_at)
                    in_temp = (out_temp * 10 + random.choice(
                        range(0, 30))) / 10.0
                    Measurement.objects.create(
                        location=box1,
                        measurement_type='in_temp',
                        measurement=in_temp,
                        observed_at=observed_at+timedelta(
                            milliseconds=500))
                for hog in range(0, NUM_HOGS_PER_BOX):
                    hog1, _ = Hog.objects.get_or_create(
                        code='hog-' + fake.ean13(),
                        name=fake.name())
                    for _ in range(0, random.choice(range(5, 100))):
                        # A random number of visits where each hog gets weighed
                        observed_at = start_date + timedelta(
                            seconds=random.choice(seconds))
                        weight = fake.weight(observed_at)
                        Measurement.objects.create(
                            hog=hog1,
                            location=box1,
                            measurement_type='weight',
                            measurement=weight,
                            observed_at=observed_at)
