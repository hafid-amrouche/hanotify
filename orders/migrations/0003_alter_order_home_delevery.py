# Generated by Django 5.0.6 on 2024-08-03 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='home_delevery',
            field=models.BooleanField(default=False),
        ),
    ]
