# Generated by Django 5.0.6 on 2024-08-10 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0039_remove_product_prices_and_images_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='has_variants',
            field=models.BooleanField(default=False),
        ),
    ]
