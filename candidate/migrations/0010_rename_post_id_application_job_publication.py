# Generated by Django 5.1.3 on 2024-12-23 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0009_alter_application_post_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='application', # Rename the field post_id to job_publication
            old_name='post_id',
            new_name='job_publication',
        ),
    ]
