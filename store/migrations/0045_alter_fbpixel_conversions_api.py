# Generated by Django 5.0.6 on 2024-09-12 06:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0044_remove_conversionsapi_fb_pixel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fbpixel',
            name='conversions_api',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversions_api', to='store.conversionsapi'),
        ),
    ]
