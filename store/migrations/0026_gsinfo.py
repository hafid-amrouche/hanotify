# Generated by Django 5.0.6 on 2024-08-18 16:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_delete_gsinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='GSInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spreadsheet_id', models.CharField(max_length=220)),
                ('sheet_name', models.CharField(max_length=220)),
                ('store', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gs_info', to='store.store')),
            ],
        ),
    ]
