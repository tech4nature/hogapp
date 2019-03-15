"""Generate some sample data to play with
"""

from datetime import date
import logging
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Box
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
            month_baselines = [3, 6, 8, 10, 18, 20, 20, 18, 14, 10, 6, 4]
            baseline = month_baselines[month-1] * 10
            return random.choice(
                range(
                    baseline, baseline + 5)) / 10.0

    fake.add_provider(Provider)
    return fake


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = make_faker()
        with transaction.atomic():
            Measurement.objects.all().delete()
            Box.objects.all().delete()
            Hog.objects.all().delete()
            for box in range(0, 10):
                for hog in range(0, 5):
                    box1, _ = Box.objects.get_or_create(
                        code='box-' + fake.ean13(),
                        name=fake.company() + " Box",
                        software_version='0.6')
                    hog1, _ = Hog.objects.get_or_create(
                        code='hog-' + fake.ean13(),
                        name=fake.name())
                    for _ in range(0, 100):
                        observed_at = fake.date_time_between_dates(
                            datetime_start=date(2018, 10, 1),
                            datetime_end=date(2019, 4, 1),
                            tzinfo=pytz.utc)
                        temperature = fake.temperature(observed_at)
                        Measurement.objects.create(
                            hog=hog1,
                            box=box1,
                            measurement_type=temperature,
                            measurement=temperature,
                            observed_at=observed_at)
