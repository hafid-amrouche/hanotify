# Generated by Django 5.0.6 on 2024-10-18 06:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0094_defaultpagesectiondesign_delete_defaultpagesection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultpagesectiondesign',
            name='home_page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='default_section_design', to='store.homepage'),
        ),
    ]
