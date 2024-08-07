# Generated by Django 3.1.4 on 2021-12-09 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20211102_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='package',
            field=models.CharField(blank=True, choices=[('Classic', 'Classic'), ('Vip', 'Vip'), ('Bonus', 'Bonus')], max_length=10),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='package_date_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='package_date_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='package_duration',
            field=models.CharField(blank=True, choices=[('1Month', '1Month'), ('3Month', '3Month'), ('6Month', '6Month')], max_length=10),
        ),
    ]
