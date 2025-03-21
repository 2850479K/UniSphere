# Generated by Django 2.2.28 on 2025-03-20 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UniSphereApp', '0009_auto_20250320_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='full_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='interests',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='languages',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='school',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='visibility',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default='public', help_text='Not shown on profile', max_length=10),
        ),
    ]
