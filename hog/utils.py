import logging
import os
import sys
import subprocess
import tempfile
from subprocess import PIPE
import redis

from rq import Queue

from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Measurement

logger = logging.getLogger(__name__)


def make_poster(measurement_id):
    measurement = Measurement.objects.get(pk=measurement_id)
    success = False
    video_location = measurement.video.url
    if "://" not in video_location:
        # We can't get it over the network; assume it's on local file
        # storage (as is the case when testing)
        video_location = measurement.video.path

    with tempfile.TemporaryDirectory() as d:
        for delta in ["0.4", "0.2", "0.1", "0"]:
            # The filter command select=gt(scene,0.3) selects the frames whose # scene detection score is greater then 0.3. We try to find the
            # most changey scene
            completed = subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    video_location,
                    "-vf",
                    "select=gt(scene\,{})".format(delta),
                    "-frames:v",
                    "1",
                    "-vsync",
                    "vfr",
                    os.path.join(d, "out%02d.jpg"),
                ],
                stdout=PIPE,
                stderr=PIPE,
            )
            if completed.returncode != 0:
                raise BaseException(
                    "Could not run ffmpeg:\n\n{}".format(completed.stderr)
                )
            try:
                with open(os.path.join(d, "out01.jpg"), "rb") as f:
                    measurement.video_poster = SimpleUploadedFile(
                        "{}.jpg".format(measurement.pk), f.read()
                    )
                    measurement.save()
                    success = True
                    logger.info(
                        "Created poster at {} at scene level {}".format(
                            measurement.video_poster.url, delta
                        )
                    )
                    break
            except FileNotFoundError:
                # The delta didn't work. Try the next one
                pass

    if not success:
        logger.warn("Unable to create poster for {}".format(measurement.video.url))

    return measurement


def delayed_make_poster(measurement):
    measurement.refresh_from_db()
    redis_url = os.getenv("REDISTOGO_URL", "redis://localhost:6379")
    conn = redis.from_url(redis_url)
    q = Queue(connection=conn)
    q.enqueue(make_poster, measurement.pk)
