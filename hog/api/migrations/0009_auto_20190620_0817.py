# Generated by Django 2.1.7 on 2019-06-20 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_hog_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='starred',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='hog',
            name='avatar',
            field=models.FileField(blank=True, help_text='Small square image of hog', null=True, upload_to='avatars'),
        ),
    ]
