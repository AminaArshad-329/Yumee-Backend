# Generated by Django 3.1.4 on 2022-02-17 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20220217_1453'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_2chance',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_guaranteed_match',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_guaranteed_match_end',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_guaranteed_match_start',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_love_coach',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_power_like',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_power_like_end',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='classic_bonus_power_like_start',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='package_name',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='vip_bonus_love_coach',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='vip_bonus_power_like',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='vip_bonus_power_like_end',
        ),
        migrations.RemoveField(
            model_name='user_profile',
            name='vip_bonus_power_like_start',
        ),
    ]
