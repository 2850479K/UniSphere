from django import forms
from .models import StudentPost, User
from django.contrib.auth.forms import UserCreationForm

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

