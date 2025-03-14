# Generated by Django 2.2.28 on 2025-03-14 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UniSphereApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentprofile',
            name='skills',
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='course',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='interests',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='school',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
