# Generated by Django 2.2.28 on 2025-03-20 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UniSphereApp', '0005_auto_20250314_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='interests',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='university',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='full_name',
            field=models.CharField(default='Not Set', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='Not Set', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='languages',
            field=models.CharField(blank=True, default='Not Set', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
