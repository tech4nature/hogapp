from unittest.mock import patch
import os

from django.test import TestCase

from rest_framework.test import APIClient

from api.models import Measurement
from utils import make_poster

from .factory import create_admin_user
from .factory import create_location
from .factory import dummy_video


class UtilTests(TestCase):
    @patch("utils.Queue")
    def test_video_creation(self, mock_queue):
        """Check we are able to POST/PUT a video
        """
        location = create_location()
        client = APIClient()
        user = create_admin_user()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/measurements/",
            {
                "measurement_type": "video",
                "observed_at": "2001-01-01T12:03+00:00",
                "location_id": location.code,
            },
            format="json",
        )
        measurement_id = response.json()["id"]
        video = dummy_video()
        response = client.put(
            "/api/measurements/{}/video/".format(measurement_id), {"video": video}
        )
        # Check the video exists
        measurement = Measurement.objects.get(pk=measurement_id)
        self.assertTrue(os.path.exists(response.json()["video"]))
        self.assertFalse(measurement.video_poster)

        # Check the poster creation is pushed to the queue
        mock_queue.return_value.enqueue.assert_called_with(make_poster, measurement_id)
