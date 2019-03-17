from django.db import models


class Hog(models.Model):
    code = models.CharField(max_length=80, primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('box', 'box'),
        ('tunnel', 'tunnel'),
    ]
    code = models.CharField(max_length=80, primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    location_type = models.CharField(
        max_length=10,
        choices=LOCATION_TYPE_CHOICES,
        db_index=True)
    software_version = models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def hogs(self):
            return Hog.objects.filter(measurement__location=self).distinct()


class Measurement(models.Model):
    MEASUREMENT_TYPE_CHOICES = [
        ('weight', 'weight'),
        ('in_temp', 'in_temp'),
        ('out_temp', 'out_temp')
    ]

    hog = models.ForeignKey(
        Hog, on_delete=models.PROTECT, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    measurement_type = models.CharField(
        max_length=10,
        choices=MEASUREMENT_TYPE_CHOICES,
        db_index=True)
    measurement = models.FloatField()
    observed_at = models.DateTimeField(db_index=True)

    def __unicode__(self):
        return "Measurement {} at {}: {}".format(
            self.measurement_type,
            self.location,
            self.measurement)

    class Meta:
        ordering = ['observed_at']
