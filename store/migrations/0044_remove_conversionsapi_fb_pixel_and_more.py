# Generated by Django 5.0.6 on 2024-09-12 06:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0043_remove_fbpixel_conversion_api_access_token_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversionsapi',
            name='fb_pixel',
        ),
        migrations.AddField(
            model_name='fbpixel',
            name='conversions_api',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conversions_api', to='store.conversionsapi'),
        ),
    ]
