# Generated by Django 5.0.6 on 2024-10-20 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0097_defaultpagesection_delete_defaultpagesectiondesign'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StoreTopPick',
        ),
    ]
