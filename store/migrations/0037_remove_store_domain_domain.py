# Generated by Django 5.0.6 on 2024-09-02 13:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_remove_store_sub_domain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='domain',
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255, unique=True)),
                ('store', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='domain', to='store.store')),
            ],
        ),
    ]
