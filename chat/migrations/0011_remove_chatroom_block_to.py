# Generated by Django 3.1.4 on 2021-12-09 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_chatroom_block_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='block_to',
        ),
    ]
