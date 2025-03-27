from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import os

# User Model
class User(AbstractUser):
    STUDENT = 'student'
    SOCIETY = 'society'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (SOCIETY, 'Society'),
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    caption = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class PostFile(models.Model):
    post = models.ForeignKey(StudentPost, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")

    def delete(self, *args, **kwargs):
        if self.file:
            storage = self.file.storage
            storage.delete(self.file.name)  
        super().delete(*args, **kwargs)

# Society & Student Profiles


def profile_picture_upload_path(instance, filename):
    return f"profile_pictures/{instance.user.username}/{filename}"

class StudentProfile(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)  
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)  
    interests = models.TextField(blank=True, null=True)  
    languages = models.CharField(max_length=255, blank=True, null=True)  
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public', help_text="Not shown on profile") 

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return "/static/images/default_pfp.jpeg"

    def __str__(self):
        return self.user.username

# Social Features
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(StudentPost, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.title[:30]}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(StudentPost, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

class Share(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(StudentPost, on_delete=models.CASCADE, related_name="shares")
    created_at = models.DateTimeField(auto_now_add=True)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Friend Request from {self.from_user.username} to {self.to_user.username}"

class SharedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    original_post = models.ForeignKey(StudentPost, on_delete=models.CASCADE, related_name="shared_posts")  
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} shared {self.original_post.title}"


class SocietyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    society_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    members = models.ManyToManyField(StudentProfile, blank=True, related_name='joined_societies')
    logo = models.ImageField(upload_to="society_logos/", blank=True, null=True)
    
    # Your new society-specific fields
    
    category = models.CharField(max_length=100, blank=True, null=True)
    social_links = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    

    def __str__(self):
        return self.society_name or self.user.username
