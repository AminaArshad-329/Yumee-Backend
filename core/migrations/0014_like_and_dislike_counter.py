# Generated by Django 3.1.4 on 2021-12-13 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20211210_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='like_and_dislike',
            name='counter',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]