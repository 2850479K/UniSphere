from django import forms
from .models import StudentPost, User, Project
from django.contrib.auth.forms import UserCreationForm
from .models import RecruiterProfile
from .models import StudentProfile
from django.contrib.auth import get_user_model  

User = get_user_model() 

class StudentPostForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False
    )  # ✅ FIXED: Indentation error removed

    class Meta:
        model = StudentPost
        fields = ['title', 'caption', 'files', 'project']  # ✅ Ensure project selection is included

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2', 'role']

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'industry', 'company_website', 'company_description', 'location']

class StudentSearchForm(forms.Form):
    name = forms.CharField(required=False, label="Student Name")
    school = forms.CharField(required=False, label="School")
    course = forms.CharField(required=False, label="Course")
    interests = forms.CharField(required=False, label="Interests")
    skills = forms.CharField(required=False, label="Skills")
