from unittest.mock import patch

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from api.models import Measurement
from .factory import create_location
from .factory import create_hog

from frontend.views import grouped_measurements


class HogViewTests(TestCase):
    @patch("utils.delayed_make_poster")
    def test_incomplete_videos(self, mock_delayed_make_poster):
        """Check we don't attempt to display videos that have not been uploaded
        """
        hog = create_hog()
        location = create_location()
        observed_at = datetime.datetime.now()
        null_video = Measurement.objects.create(
            hog=hog,
            location=location,
            measurement_type="video",
            observed_at=observed_at,
        )
        uploaded_video = Measurement.objects.create(
            hog=hog,
            location=location,
            measurement_type="video",
            observed_at=observed_at,
            video=SimpleUploadedFile("hog.mp4", b"these are the file contents!"),
        )
        measurements = grouped_measurements(hog=hog.code)
        self.assertEqual(
            measurements, [{"header": uploaded_video, "video": uploaded_video}]
        )
