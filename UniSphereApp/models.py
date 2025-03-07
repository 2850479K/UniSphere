from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    company_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    company_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    interests = models.TextField()
    skills = models.TextField()
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username