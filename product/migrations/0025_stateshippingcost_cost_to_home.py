# Generated by Django 5.0.6 on 2024-08-06 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0024_remove_product_variants_combinations'),
    ]

    operations = [
        migrations.AddField(
            model_name='stateshippingcost',
            name='cost_to_home',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
