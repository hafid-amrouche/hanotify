# Generated by Django 5.0.6 on 2024-07-26 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0006_alter_category_icon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='icon',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='title',
            new_name='label',
        ),
    ]
