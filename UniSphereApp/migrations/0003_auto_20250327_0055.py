# Generated by Django 2.2.28 on 2025-03-27 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UniSphereApp', '0002_auto_20250326_2328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='societyprofile',
            name='logo',
        ),
        migrations.AddField(
            model_name='societyprofile',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='joined_societies', to='UniSphereApp.StudentProfile'),
        ),
    ]
