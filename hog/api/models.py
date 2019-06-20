from django.contrib.gis.db import models
from django.core.validators import validate_slug
from faker import Faker


class Hog(models.Model):
    code = models.CharField(max_length=80, primary_key=True, validators=[validate_slug])
    name = models.CharField(max_length=200, blank=True, null=True)
    avatar = models.FileField(
        blank=True,
        null=True,
        upload_to="avatars",
        help_text="Small square image of hog",
    )

    def __str__(self):
        return self.name

    def locations(self):
        return Location.objects.filter(measurement__hog=self).distinct()


class Location(models.Model):
    LOCATION_TYPE_CHOICES = [("box", "box"), ("tunnel", "tunnel")]
    code = models.CharField(max_length=80, primary_key=True, validators=[validate_slug])
    name = models.CharField(max_length=200, blank=True, null=True)
    location_type = models.CharField(
        max_length=10, choices=LOCATION_TYPE_CHOICES, db_index=True
    )
    software_version = models.CharField(max_length=5, blank=True, null=True)
    coords = models.PointField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def hogs(self):
        return Hog.objects.filter(measurement__location=self).distinct()


class Measurement(models.Model):
    MEASUREMENT_TYPE_CHOICES = [
        ("video", "video"),
        ("weight", "weight"),
        ("in_temp", "in_temp"),
        ("out_temp", "out_temp"),
    ]

    hog = models.ForeignKey(Hog, on_delete=models.PROTECT, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    measurement_type = models.CharField(
        max_length=10, choices=MEASUREMENT_TYPE_CHOICES, db_index=True
    )
    measurement = models.FloatField(blank=True, null=True)
    video = models.FileField(blank=True, null=True, upload_to="videos")
    video_poster = models.FileField(blank=True, null=True, upload_to="posters")
    observed_at = models.DateTimeField(db_index=True)
    starred = models.BooleanField(db_index=True, default=False)

    def __str__(self):
        return "{}:{} at {}".format(
            self.measurement_type, self.measurement, self.location
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            try:
                self.hog
            except Hog.DoesNotExist:
                fake = Faker()
                self.hog = Hog.objects.create(code=self.hog_id, name=fake.name())
        super(Measurement, self).save(*args, **kwargs)

    class Meta:
        ordering = ["observed_at"]
