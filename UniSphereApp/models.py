from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    STUDENT = 'student'
    RECRUITER = 'recruiter'
    SOCIETY = 'society'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (RECRUITER, 'Recruiter'),
        (SOCIETY, 'Society'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    is_public = models.BooleanField(default=True)
    school = models.CharField(max_length=100, blank=True)
    course = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    def __str__(self):
        return self.username

class StudentPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    caption = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class PostFile(models.Model):
    post = models.ForeignKey('StudentPost', related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")

class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    company_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    company_website = models.URLField(blank=True, null=True)
    def __str__(self):
        return self.company_name

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    school = models.CharField(max_length=255, blank=True)
    course = models.CharField(max_length=255, blank=True)
    interests = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    def __str__(self):
        return self.user.username



