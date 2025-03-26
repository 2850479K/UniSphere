from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import StudentPost, Project, StudentProfile, Comment, FriendRequest, SocietyProfile

User = get_user_model()

# User & Authentication Forms
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

# Profile Forms
class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['full_name', 'gender', 'profile_picture']


class StudentProfileForm(forms.ModelForm):
    delete_picture = forms.BooleanField(required=False, label="Delete profile picture")

    class Meta:
        model = StudentProfile
        fields = ["profile_picture", "full_name", "gender", "school", "bio", "interests", "languages", "visibility"]

class EditProfileForm(forms.ModelForm):
    university = forms.CharField(required=False, label="University")
    bio = forms.CharField(widget=forms.Textarea, required=False, label="Bio")
    interests = forms.CharField(required=False, label="Interests")
    languages = forms.CharField(required=False, label="Languages Spoken")

    class Meta:
        model = StudentProfile
        fields = ['profile_picture', 'university', 'bio', 'interests', 'languages']

# Project & Post Forms
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']

class StudentPostForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False
    )

    class Meta:
        model = StudentPost
        fields = ['title', 'caption']
        required = {
            'files': False
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

# Student Search Forms


class StudentSearchForm(forms.Form):
    name = forms.CharField(required=False, label="Student Name")
    school = forms.CharField(required=False, label="School")
    course = forms.CharField(required=False, label="Course")
    interests = forms.CharField(required=False, label="Interests")
    skills = forms.CharField(required=False, label="Skills")


class SocietyProfileForm(forms.ModelForm):
    class Meta:
        model = SocietyProfile
        fields = [
            'society_name',
            'description',
            'website',
            'category',
            'social_links',
            'contact_email',
        ]
