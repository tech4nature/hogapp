from unittest.mock import patch
import os

from django.conf import settings
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

    @patch("utils.Queue")
    @patch("botocore.client.BaseClient._make_api_call")
    def test_video_creation_s3(self, mock_boto, mock_queue):
        """Check we are able to POST/PUT a video when using the s3 backend we
        use in production

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
        with self.settings(
            DEFAULT_FILE_STORAGE="storages.backends.s3boto3.S3Boto3Storage"
        ):
            response = client.put(
                "/api/measurements/{}/video/".format(measurement_id), {"video": video}
            )
        # Check the video exists
        measurement = Measurement.objects.get(pk=measurement_id)
        expected_extension = video.name.split(".")[-1]
        # 'https://hogapp.s3.amazonaws.com/videos/1.mp4'
        expected_url = "https://{}.s3.amazonaws.com/{}/{}.{}".format(
            settings.AWS_STORAGE_BUCKET_NAME,
            settings.AWS_VIDEO_BUCKET,
            measurement_id,
            expected_extension,
        )
        self.assertEqual(response.json()["video"], expected_url)
        self.assertFalse(measurement.video_poster)

        # Check the poster creation is pushed to the queue
        mock_queue.return_value.enqueue.assert_called_with(make_poster, measurement_id)
