# Generated by Django 3.1.4 on 2022-09-06 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_user_profile_is_banned'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='is_restored',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
