"""Generate some sample data to play with
"""

import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Box
from api.models import Hog
from api.models import Measurement


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            box1, _ = Box.objects.get_or_create(
                code="A1234",
                name="Happyland Box",
                software_version='0.6')
            hog1, _ = Hog.objects.get_or_create(code='hog-abc123', name='Mrs Tiggywinkle')
            Measurement.objects.create(
                hog=hog1,
                box=box1,
                measurement_type='weight',
                measurement=350.3,
                observed_at="2018-01-01 15:00")
            Measurement.objects.create(
                hog=hog1,
                box=box1,
                measurement_type='weight',
                measurement=360.3,
                observed_at="2018-01-02 15:00")
            Measurement.objects.create(
                hog=hog1,
                box=box1,
                measurement_type='weight',
                measurement=361.3,
                observed_at="2018-01-02 16:00")
            Measurement.objects.create(
                hog=hog1,
                box=box1,
                measurement_type='in_temp',
                measurement=16.1,
                observed_at="2018-01-01 15:00")
            Measurement.objects.create(
                hog=hog1,
                box=box1,
                measurement_type='out_temp',
                measurement=15.6,
                observed_at="2018-01-01 15:00")
