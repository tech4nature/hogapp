from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from api.models import Measurement
from .factory import create_location
from .factory import create_hog
from .factory import dummy_video

from utils import make_poster


class UtilTests(TestCase):
    def test_poster_generation(self):
        """Check we are able to generate a poster
        """
        hog = create_hog()
        location = create_location()
        observed_at = timezone.now()
        with dummy_video() as f:
            uploaded_video = Measurement.objects.create(
                hog=hog,
                location=location,
                measurement_type="video",
                observed_at=observed_at,
                video=SimpleUploadedFile("hog.mp4", f.read()),
            )
        make_poster(uploaded_video.pk)
        uploaded_video.refresh_from_db()
        self.assertTrue(uploaded_video.video_poster)
