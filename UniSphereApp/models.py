from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# Create your models here.

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

class StudentPost(models.Model):
    #link the post to the user (check with jiacheng and reem for the users)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    caption = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #check the slicing to 30
        #displat username + caption in admin
        return f"{self.user.username} - {self.caption[:30]}"

class PostFile(models.Model):
    #link files to the post
    post = models.ForeignKey(StudentPost, related_name="files", on_delete=models.CASCADE)
    #uploads diles to "upload/" directory
    file = models.FileField(upload_to="uploads/")




