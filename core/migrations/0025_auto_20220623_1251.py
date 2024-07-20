# Generated by Django 3.1.4 on 2022-06-23 07:51

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_user_profile_remaining_days_in_exp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile',
            name='cross_user_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), blank=True, default=list, size=None),
        ),
        migrations.AlterField(
            model_name='user_profile',
            name='package_duration',
            field=models.CharField(blank=True, choices=[('1 Month', '1 Month'), ('3 Month', '3 Month'), ('6 Month', '6 Month'), ('15 Days Trial', '15 Days Trial')], default='15 Days Trial', max_length=100),
        ),
        migrations.AlterField(
            model_name='user_profile',
            name='passion',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200, null=True), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='user_profile',
            name='time_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.DateTimeField(blank=True, max_length=100, null=True), blank=True, default=list, size=None),
        ),
    ]