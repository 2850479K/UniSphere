from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import StudentPost, Project, RecruiterProfile, StudentProfile, Comment, FriendRequest

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

# Recruiter Profile & Student Search Forms
class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'industry', 'company_website', 'company_description', 'location']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['company_name', 'industry', 'company_website', 'company_description', 'location']

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required!")

        return cleaned_data

class StudentSearchForm(forms.Form):
    name = forms.CharField(required=False, label="Student Name")
    school = forms.CharField(required=False, label="School")
    course = forms.CharField(required=False, label="Course")
    interests = forms.CharField(required=False, label="Interests")
    skills = forms.CharField(required=False, label="Skills")

# Social
class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = []
