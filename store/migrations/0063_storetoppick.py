# Generated by Django 5.0.6 on 2024-09-21 16:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0043_alter_product_options'),
        ('store', '0062_delete_storetoppick'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreTopPick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='top_picks', to='store.store')),
            ],
        ),
    ]
