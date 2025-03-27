from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from UniSphereApp.forms import *
from UniSphereApp.models import User, StudentProfile, SocietyProfile, Project, StudentPost, Comment

class FormTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(username='teststudent', password='pass1234', role='student')
        self.society_user = User.objects.create_user(username='testsociety', password='pass1234', role='society')

    # User & Authentication
    def test_user_register_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 'student'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    #  Student Profile
    def test_create_profile_form(self):
        form = CreateProfileForm(data={'full_name': 'Test Name', 'gender': 'male'})
        self.assertTrue(form.is_valid())

    def test_student_profile_form_with_delete_picture(self):
        form_data = {
            'full_name': 'Test Student',
            'gender': 'female',
            'school': 'Test School',
            'bio': 'Test bio',
            'interests': 'Coding, Music',
            'languages': 'English',
            'visibility': 'public',
            'delete_picture': True
        }
        form = StudentProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data.get('delete_picture'))

    def test_edit_profile_form(self):
        form_data = {
            'university': 'Test Uni',
            'bio': 'Edit Bio',
            'interests': 'Reading',
            'languages': 'Chinese'
        }
        form = EditProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Project & Post
    def test_project_form(self):
        form = ProjectForm(data={'title': 'Test Project', 'description': 'Test Description'})
        self.assertTrue(form.is_valid())

    def test_student_post_form_with_files(self):
        form = StudentPostForm(data={'title': 'Test Post', 'caption': 'Testing...'}, files={})
        self.assertTrue(form.is_valid())

    # Comment
    def test_comment_form(self):
        form = CommentForm(data={'content': 'This is a comment'})
        self.assertTrue(form.is_valid())

    # Search
    def test_search_user_form_partial_input(self):
        form_data = {'username': 'abc', 'skills': 'Python'}
        form = SearchUserForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Society
    def test_society_profile_form(self):
        form_data = {
            'society_name': 'Drama Club',
            'description': 'Theater group',
            'website': 'https://drama.com',
            'category': 'Arts',
            'social_links': 'https://instagram.com/drama',
            'contact_email': 'drama@uni.com',
        }
        form = SocietyProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_society_create_profile_form(self):
        form = SocietyCreateProfileForm(data={'society_name': 'Music Society'})
        self.assertTrue(form.is_valid())
