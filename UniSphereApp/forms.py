from django import forms
from .models import StudentPost, User
from django.contrib.auth.forms import UserCreationForm
from .models import RecruiterProfile
from .models import StudentProfile

#create form for a new post
class StudentPostForm(forms.ModelForm):
    files = forms.FileField(
        #allow for mulitple uploads
        widget=forms.ClearableFileInput(attrs={'multiple':True}), required=False)

    class Meta:
        model = StudentPost
        fields = ['caption', 'files']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
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
