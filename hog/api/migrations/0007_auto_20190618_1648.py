# Generated by Django 2.1.7 on 2019-06-18 16:48

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_location_coords'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='video_poster',
            field=models.FileField(blank=True, null=True, upload_to='posters'),
        ),
        migrations.AlterField(
            model_name='hog',
            name='code',
            field=models.CharField(max_length=80, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')]),
        ),
        migrations.AlterField(
            model_name='location',
            name='code',
            field=models.CharField(max_length=80, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')]),
        ),
    ]
