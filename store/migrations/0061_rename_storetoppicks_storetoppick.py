# Generated by Django 5.0.6 on 2024-09-21 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0043_alter_product_options'),
        ('store', '0060_storetoppicks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StoreTopPicks',
            new_name='StoreTopPick',
        ),
    ]
