# Generated by Django 5.0.6 on 2024-08-06 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_alter_relatedproduct_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ask_for_address',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='ask_for_city',
            field=models.BooleanField(default=True),
        ),
    ]
