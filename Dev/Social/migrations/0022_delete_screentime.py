# Generated by Django 4.2.6 on 2024-02-02 08:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Social', '0021_remove_screentime_time_screentime_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ScreenTime',
        ),
    ]
