# Generated by Django 5.0.6 on 2024-10-14 05:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0044_product_usedefaultshipping'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='useDefaultShipping',
            new_name='use_default_shipping',
        ),
    ]
