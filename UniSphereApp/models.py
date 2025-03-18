from email.policy import default

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from setuptools.command.easy_install import auto_chmod
from django.contrib.auth.models import AbstractUser
import os


# User Model
class User(AbstractUser):
    STUDENT = 'student'
    RECRUITER = 'recruiter'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (RECRUITER, 'Recruiter'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)

    def __str__(self):
        return self.username

# Projects & Posts
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class StudentPost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    caption = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class PostFile(models.Model):
    post = models.ForeignKey(StudentPost, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")

# Recruiter & Student Profiles
class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    company_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    company_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.company_name

def profile_picture_upload_path(instance, filename):
    return f"profile_pictures/{instance.user.username}/{filename}"

class StudentProfile(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    languages = models.CharField(max_length=255, blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')  

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return "/static/images/default_pfp.jpeg"

    def delete_profile_picture(self):
        if self.profile_picture and os.path.isfile(self.profile_picture.path):
            os.remove(self.profile_picture.path)
        self.profile_picture = None
        self.save()

    def __str__(self):
        return self.user.username

class Invitation(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='received_invitations')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation from {self.recruiter.username} to {self.student.user.username}"

