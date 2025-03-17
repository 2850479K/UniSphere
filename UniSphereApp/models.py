from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
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
    title = models.CharField(max_length=255)
    caption = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        #check the slicing to 30
        #displat username + caption in admin
        return f"{self.user.username} - {self.title}"

class PostFile(models.Model):
    #link files to the post
    post = models.ForeignKey('StudentPost', related_name="files", on_delete=models.CASCADE)
    #uploads diles to "upload/" directory
    file = models.FileField(upload_to="uploads/")

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

# New code adding on social features

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('StudentPost', on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.title[:30]}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('StudentPost', on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.post.title[:30]}"


class Share(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('StudentPost', on_delete=models.CASCADE, related_name="shares")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} shared {self.post.title[:30]}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Friend Request from {self.from_user.username} to {self.to_user.username}"


class SharedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    original_post = models.ForeignKey('StudentPost', on_delete=models.CASCADE, related_name="shared_posts")  
    timestamp = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):
        return f"{self.user.username} shared {self.original_post.title}"





