# Generated by Django 5.0.6 on 2024-10-02 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0069_rename_imageobejcts_homepagesection_image_obejcts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepagesection',
            old_name='image_obejcts',
            new_name='image_objects',
        ),
    ]
