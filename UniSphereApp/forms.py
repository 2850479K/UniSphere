from django import forms
from .models import StudentPost

#create form for a new post
class StudentPostForm(forms.ModelForm):
    files = forms.FileField(
        #allow for mulitple uploads
        widget=forms.ClearableFileInput(attrs={'multiple':True}), required=False)

    class Meta:
        model = StudentPost
        fields = ['caption', 'files']
