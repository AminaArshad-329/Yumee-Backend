# Generated by Django 3.1.4 on 2022-03-15 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20220314_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile',
            name='education',
            field=models.CharField(blank=True, choices=[('College', 'College'), ('High School', 'High School'), ('BAC Level', 'BAC Level'), ('University Diploma', 'University Diploma'), ('update_education_highschool_checkbox', 'update_education_highschool_checkbox')], max_length=200),
        ),
    ]
