# Generated by Django 5.0.6 on 2024-07-29 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_product_prices_and_images_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='prices_and_images_list',
            field=models.TextField(blank=True, null=True),
        ),
    ]
