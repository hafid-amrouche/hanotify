# Generated by Django 5.0.6 on 2024-10-20 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0045_rename_usedefaultshipping_product_use_default_shipping'),
        ('store', '0099_delete_vipstore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepagesection',
            name='products',
            field=models.ManyToManyField(blank=True, null=True, to='product.product'),
        ),
    ]
