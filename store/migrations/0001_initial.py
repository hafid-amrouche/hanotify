# Generated by Django 5.0.6 on 2024-07-12 07:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('others', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_color', models.CharField(default='#c8102e', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('domain', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('policies', models.JSONField(blank=True, null=True)),
                ('phone_numbers', models.JSONField()),
                ('facebook', models.TextField(blank=True, null=True)),
                ('instagram', models.TextField(blank=True, null=True)),
                ('youtube', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='others.location')),
                ('logo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='others.image')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stores', to=settings.AUTH_USER_MODEL)),
                ('seo', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='others.seo')),
            ],
        ),
    ]
