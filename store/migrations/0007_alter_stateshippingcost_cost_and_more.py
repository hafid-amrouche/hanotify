# Generated by Django 5.0.6 on 2024-08-09 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_stateshippingcost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stateshippingcost',
            name='cost',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='stateshippingcost',
            name='cost_to_home',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]
