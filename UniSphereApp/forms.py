from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import StudentPost, User, RecruiterProfile, StudentProfile

class StudentPostForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.FileInput(),
        required=False
    )
    class Meta:
        model = StudentPost
        fields = ['title', 'caption', 'files']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'industry', 'company_website', 'company_description', 'location']

class ProfileEdiForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_public', 'first_name', 'last_name', 'school', 'course', 'interests', 'profile_picture']

class StudentSearchForm(forms.Form):
    name = forms.CharField(required=False, label="Student Name")
    school = forms.CharField(required=False, label="School")
    course = forms.CharField(required=False, label="Course")
    interests = forms.CharField(required=False, label="Interests")
    skills = forms.CharField(required=False, label="Skills")
