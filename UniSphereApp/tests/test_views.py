from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth import get_user_model
from UniSphereApp.forms import ProjectForm, SocietyCreateProfileForm
from django.contrib.messages import get_messages
from UniSphereApp.models import User, StudentProfile, StudentPost, Project, PostFile, SocietyProfile, Comment, Share, Comment, FriendRequest, Repost, Like
import shutil
import os
from django.conf import settings
from UniSphereApp.views import get_friends

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        self.initial_files = set(os.listdir(self.upload_dir))

        # student1
        self.student1_user = User.objects.create_user(
            username='student1',
            password='pass1234',
            role='student'
        )
        self.student1_profile = StudentProfile.objects.create(
            user=self.student1_user,
            full_name="Alice Django",
            school="Test University",
            course="CS101",
            interests="Django",
            skills="Python"
        )

        # society1
        self.society_user = User.objects.create_user(
            username='society1',
            password='pass1234',
            role='society'
        )
        self.society_profile = SocietyProfile.objects.create(
            user=self.society_user,
            society_name="Tech Society",
            category="Technology",
            description="A tech group",
            contact_email="society@example.com"
        )

        self.client.login(username='student1', password='pass1234')

        self.project = Project.objects.create(
            user=self.student1_user,
            title='Test Project',
            description='A test project'
        )

        self.post = StudentPost.objects.create(
            user=self.student1_user,
            title='Post',
            caption='Cap',
            project=self.project
        )

        self.profile_post = StudentPost.objects.create(
            user=self.student1_user,
            title='Profile Post',
            caption='For profile',
            project=None
        )

        self.test_file = SimpleUploadedFile(
            "test_file.txt", b"file_content", content_type="text/plain"
        )

        # testuser1
        self.test_user1 = User.objects.create_user(username='testuser', password='testpass', role='student')
        self.test_profile1 = StudentProfile.objects.create(user=self.test_user1)

        # frienduser
        self.friend_user = User.objects.create_user(username='frienduser', password='testpass', role='student')
        self.friend_profile = StudentProfile.objects.create(user=self.friend_user)

        # student2
        self.student2_user = User.objects.create_user(username='student2', password='pass1234', role='student')
        self.student2_profile = StudentProfile.objects.create(user=self.student2_user)

        # testuser2
        self.test_user2 = User.objects.create_user(username='testuser2', password='testpass2', role='student')
        self.test_profile2 = StudentProfile.objects.create(user=self.test_user2)

    def tearDown(self):
        current_files = set(os.listdir(self.upload_dir))
        new_files = current_files - self.initial_files
        for file_name in new_files:
            file_path = os.path.join(self.upload_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)


        # General Views
    def test_home_redirect_for_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('welcomepage'))

    def test_home_render_for_logged_in_user(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/home.html')

    def test_welcomepage_view(self):
        response = self.client.get(reverse('welcomepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/welcomepage.html')

    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/register.html')

    def test_register_post_valid(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'role': 'student',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('create_profile'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    # Login
    def test_login_valid(self):
        response = self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'pass1234'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'student1'}))
        self.assertTemplateUsed(response, 'UniSphereApp/student_profile.html')

        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully logged in" in str(m) for m in messages_list))

    def test_login_invalid(self):
        self.client.logout()

        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'invalidpass'
        })
        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Invalid username or password" in str(m) for m in messages)
        )

    def test_profile_posts_student(self):
        StudentPost.objects.create(
            user=self.student1_user,
            title='Post 1',
            caption='Caption'
        )
        url = reverse('profile_posts', kwargs={'username': self.student1_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/profile_posts.html')
        self.assertIn('posts', response.context)
        self.assertEqual(response.context['profile'].user, self.student1_user)

    def test_profile_posts_society(self):
        url = reverse('profile_posts', kwargs={'username': self.society_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/profile_posts.html')
        self.assertIn('posts', response.context)
        self.assertEqual(response.context['profile'].user, self.society_user)

    def test_profile_posts_unknown_role(self):
        unknown_user = User.objects.create_user(username='unknown', password='12345', role='unknown')
        url = reverse('profile_posts', kwargs={'username': unknown_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/profile_posts.html')
        self.assertIn('posts', response.context)
        self.assertIsNone(response.context['profile'])

    def test_create_profile_society_get(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/create_profile.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], SocietyCreateProfileForm)


    def test_create_profile_student_post(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.post(url, {
            'full_name': 'New Name',
            'gender': 'male'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudentProfile.objects.filter(user=self.student1_user).exists())

    def test_create_profile_society_post(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.post(url, {
            'society_name': 'Official Society',
            'contact_email': 'official_society@example.com'
        })
        self.assertEqual(response.status_code, 302)

        profile = SocietyProfile.objects.get(user=self.society_user)
        self.assertEqual(profile.society_name, 'Official Society')
        self.assertEqual(profile.contact_email, 'official_society@example.com')

    # Profile View
    def test_profile_view_as_owner_student(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': self.student1_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/student_profile.html')


    def test_profile_view_as_other_student_private(self):
        self.student2_profile.visibility = 'private'
        self.student2_profile.save()

        self.client.login(username='testuser', password='testpass')
        url = reverse('profile', kwargs={'username': self.student2_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/private_profile.html')

    def test_profile_view_society(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': self.society_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/society_profile.html')

    def test_society_profile_view_get(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('profile', kwargs={'username': self.society_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/society_profile.html')
        self.assertIn('is_member', response.context)
        self.assertFalse(response.context['is_member'])

    def test_society_profile_join_post(self):
        self.client.login(username='student2', password='pass1234')
        url = reverse('profile', kwargs={'username': self.society_user.username})
        response = self.client.post(url, {'action': 'join'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.society_profile.members.filter(id=self.student2_profile.id).exists())

    def test_society_profile_leave_post(self):
        self.society_profile.members.add(self.student2_profile)
        self.client.login(username='student2', password='pass1234')

        url = reverse('profile', kwargs={'username': self.society_user.username})
        response = self.client.post(url, {'action': 'leave'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.society_profile.members.filter(id=self.student2_profile.id).exists())

    def test_profile_view_as_friend(self):
        self.student1_profile.friends.add(self.student2_profile)

        self.client.login(username='student2', password='pass1234')
        url = reverse('profile', kwargs={'username': self.student1_user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/student_profile.html')
        self.assertTrue(response.context['is_friend'])

    def test_profile_view_friend_request_sent(self):
        FriendRequest.objects.create(from_user=self.student2_user, to_user=self.student1_user, status='pending')

        self.client.login(username='student2', password='pass1234')
        url = reverse('profile', kwargs={'username': self.student1_user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/student_profile.html')
        self.assertTrue(response.context['friend_request_sent'])

    def test_profile_view_student_profile_does_not_exist(self):
        no_profile_user = User.objects.create_user(username='noprofile', password='testpass', role='student')
        self.client.login(username='noprofile', password='testpass')

        url = reverse('profile', kwargs={'username': self.student1_user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/student_profile.html')

        self.assertFalse(response.context['is_friend'])
        self.assertFalse(response.context['friend_request_sent'])

    # Remove friend
    def test_remove_friend_post(self):
        self.student1_profile.friends.add(self.student2_profile)
        self.student2_profile.friends.add(self.student1_profile)

        self.client.login(username='student1', password='pass1234')
        url = reverse('remove_friend', kwargs={'user_id': self.student2_user.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('friend_requests', kwargs={'username': 'student1'}))

        self.student1_profile.refresh_from_db()
        self.student2_profile.refresh_from_db()

        self.assertFalse(self.student1_profile.friends.filter(id=self.student2_profile.id).exists())
        self.assertFalse(self.student2_profile.friends.filter(id=self.student1_profile.id).exists())

    def test_remove_friend_invalid_method(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('remove_friend', kwargs={'user_id': self.student2_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friend_requests', kwargs={'username': 'student1'}))

    def test_remove_friend_invalid_user(self):
        self.client.login(username='student1', password='pass1234')
        invalid_user_id = 9999

        url = reverse('remove_friend', kwargs={'user_id': invalid_user_id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

    def test_remove_friend_exception_handled(self):
        self.client.login(username='student1', password='pass1234')

        self.student2_profile.delete()

        url = reverse('remove_friend', kwargs={'user_id': self.student2_user.id})
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/friend_requests.html')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("went wrong" in str(m) for m in messages))


    #My profile
    def test_my_profile_redirect(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('my_profile'))
        self.assertRedirects(response, reverse('profile', kwargs={'username': self.student1_user.username}))

    def test_edit_profile_get(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('edit_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_profile.html')
        self.assertIn('form', response.context)

    def test_edit_profile_post(self):
        self.client.login(username='student2', password='pass1234')
        url = reverse('edit_profile')
        response = self.client.post(url, {
            'full_name': 'New Name',
            'gender': 'male',
            'school': 'New School',
            'bio': 'Updated bio',
            'interests': 'coding',
            'languages': 'English',
            'visibility': 'public',
        })
        self.assertRedirects(response, reverse('profile', kwargs={'username': self.student2_user.username}))
        self.student2_profile.refresh_from_db()
        self.assertEqual(self.student2_profile.full_name, 'New Name')

    def test_edit_project_invalid_post(self):
        self.client.login(username='student1', password='pass1234')

        url = reverse('edit_project', kwargs={'project_id': self.project.id})

        response = self.client.post(url, {
            'title': '',
            'description': 'Missing title so this should fail.'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_project.html')

        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error updating project" in str(m) for m in messages_list))

    #Portfolios & Projects
    def test_user_portfolio_view(self):
        self.client.login(username='student2', password='pass1234')

        project = Project.objects.create(
            user=self.student2_user,
            title='Test Project',
            description='Project description here'
        )

        url = reverse('user_portfolio', kwargs={'username': self.student2_user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/portfolio.html')
        self.assertIn('projects', response.context)
        self.assertIn(project, response.context['projects'])

    def test_project_detail_view(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('project', kwargs={'project_id': self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/project.html')
        self.assertEqual(response.context['project'], self.project)

    def test_create_project_get(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('create_project'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/create_project.html')
        self.assertIsInstance(response.context['form'], ProjectForm)

    def test_create_project_post_success(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(reverse('create_project'), {
            'title': 'New Project',
            'description': 'New Description',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(title='New Project', user=self.student1_user).exists())

    def test_create_project_post_fail(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(reverse('create_project'), {
            'title': '',  # Invalid
            'description': 'Some Desc',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'This field is required.')

    def test_edit_project_get(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('edit_project', kwargs={'project_id': self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_project.html')
        self.assertEqual(response.context['project'], self.project)

    def test_edit_project_post_success(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('edit_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url, {
            'title': 'Updated Title',
            'description': 'Updated Desc'
        })

        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Title')

    def test_edit_project_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='pass1234', role='student')
        self.client.login(username='other', password='pass1234')

        url = reverse('edit_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url, {
            'title': 'Hacked',
            'description': 'Unauthorized edit'
        })

        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))
        self.project.refresh_from_db()
        self.assertNotEqual(self.project.title, 'Hacked')

    def test_delete_project_post(self):
        self.client.login(username='student1', password='pass1234')

        url = reverse('delete_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url)

        self.assertRedirects(
            response,
            reverse('user_portfolio', kwargs={'username': self.student1_user.username})
        )
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_get_redirect(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('delete_project', kwargs={'project_id': self.project.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))

    def test_delete_project_unauthorized_user(self):
        self.client.login(username='testuser', password='testpass')

        url = reverse('delete_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))

        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("not authorized to delete" in str(m) for m in messages_list))


    #Post
    def test_create_post_get(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('create_post', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_post_post_valid(self):
        self.client.login(username='student1', password='pass1234')
        file = SimpleUploadedFile("file.txt", b"file_content")
        response = self.client.post(
            reverse('create_post', args=[self.project.id]),
            data={'title': 'New Post', 'caption': 'New Cap', 'files': file},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(StudentPost.objects.filter(title='New Post').exists())


    def test_edit_post_get(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('edit_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_post_post_valid(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(
            reverse('edit_post', args=[self.post.id]),
            data={'title': 'Updated Title', 'caption': 'Cap'}
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_edit_post_unauthorized_redirects(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('edit_post', args=[self.post.id]), follow=True)
        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.post.project.id}))
        self.assertContains(response, "You are not authorized to edit this post.")

    def test_edit_post_unauthorized_redirects_to_profile_when_no_project(self):
        self.profile_post.user = self.test_user1
        self.profile_post.save()
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('edit_post', args=[self.profile_post.id]), follow=True)
        self.assertRedirects(response, reverse('profile', kwargs={'username': self.test_user1.username}))

    def test_edit_post_with_file_upload(self):
        self.client.login(username='student1', password='pass1234')

        file = SimpleUploadedFile("newfile.txt", b"new content", content_type="text/plain")

        response = self.client.post(
            reverse('edit_post', args=[self.post.id]),
            data={
                'title': 'Updated Title',
                'caption': 'Updated caption',
                'files': [file]
            },
            follow=True
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

        self.assertTrue(PostFile.objects.filter(post=self.post, file='uploads/newfile.txt').exists())

        if self.post.project:
            expected_url = reverse('project', kwargs={'project_id': self.post.project.id})
        else:
            expected_url = reverse('profile', kwargs={'username': self.post.user.username})

        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)


    def test_delete_post_post(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('project', args=[self.project.id]))
        self.assertFalse(StudentPost.objects.filter(id=self.post.id).exists())

    def test_delete_post_unauthorized_redirects_to_project(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('delete_post', args=[self.post.id]), follow=True)
        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))
        self.assertContains(response, "You are not authorized to delete this post.")

    def test_delete_post_unauthorized_redirects_to_profile_when_no_project(self):
        self.profile_post.user = self.test_user1
        self.profile_post.save()
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('delete_post', args=[self.profile_post.id]), follow=True)
        self.assertRedirects(response, reverse('profile', kwargs={'username': self.test_user1.username}))

    def test_delete_post_post_redirects_to_profile_when_no_project(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(reverse('delete_post', args=[self.profile_post.id]), follow=True)
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'student1'}))
        self.assertFalse(StudentPost.objects.filter(id=self.profile_post.id).exists())

    def test_delete_post_get_redirects_to_project(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('delete_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))

    def test_delete_post_get_redirects_to_profile_when_no_project(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('delete_post', args=[self.profile_post.id]))
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'student1'}))

    def test_view_post(self):
        response = self.client.get(reverse('view_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)


    # Search
    def test_search_users_empty(self):
        response = self.client.get(reverse('search_users'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_results'])

    def test_search_users_student_match(self):
        self.student1_profile.interests = "Django"
        self.student1_profile.save()

        response = self.client.get(reverse('search_users'), {'interests': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertIn(self.student1_profile, response.context['students'])

    def test_search_users_student_by_school(self):
        response = self.client.get(reverse('search_users'), {'school': 'Test University'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student1_profile, response.context['students'])

    def test_search_users_student_by_skills(self):
        response = self.client.get(reverse('search_users'), {'skills': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student1_profile, response.context['students'])

    def test_search_users_society_match(self):
        response = self.client.get(reverse('search_users'), {'society_name': 'Tech Society'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertIn(self.society_profile, response.context['societies'])

    def test_search_users_society_by_category(self):
        response = self.client.get(reverse('search_users'), {'category': 'Technology'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.society_profile, response.context['societies'])

    def test_search_users_society_by_email(self):
        response = self.client.get(reverse('search_users'), {'contact_email': 'society@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.society_profile, response.context['societies'])

    def test_search_users_combined(self):
        response = self.client.get(reverse('search_users'), {
            'school': 'Test University',
            'society_name': 'Tech Society'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student1_profile, response.context['students'])
        self.assertIn(self.society_profile, response.context['societies'])

    def test_search_users_student_by_username_and_name(self):
        self.student1_profile.full_name = "Test Student"
        self.student1_profile.save()

        response = self.client.get(reverse('search_users'), {
            'username': 'student1',
            'name': 'Test Student'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student1_profile, response.context['students'])
        self.assertTrue(response.context['show_results'])

    def test_search_users_student_by_course_and_skills(self):
        self.student1_profile.course = "CS"
        self.student1_profile.skills = "Python"
        self.student1_profile.save()

        response = self.client.get(reverse('search_users'), {
            'course': 'CS',
            'skills': 'Python'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student1_profile, response.context['students'])
        self.assertTrue(response.context['show_results'])

    def test_search_users_society_by_username_and_description(self):
        self.society_profile.description = "A tech group"
        self.society_profile.save()

        response = self.client.get(reverse('search_users'), {
            'username': 'society1',
            'description': 'A tech group'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.society_profile, response.context['societies'])
        self.assertTrue(response.context['show_results'])


    # Social Features
    def test_get_comments(self):
        Comment.objects.create(user=self.test_user1, post=self.post, content='Great!')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('get_comments', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.json())

    def test_add_comment(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('add_comment', args=[self.post.id]),
            {'content': 'Nice post!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(post=self.post).exists())

    def test_view_all_comments(self):
        Comment.objects.create(user=self.test_user1, post=self.post, content='Another comment')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('view_all_comments', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/all_comments.html')


    # like
    def test_like_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('like_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])

    def test_unlike_post(self):
        self.client.login(username='testuser', password='testpass')
        Like.objects.create(user=self.test_user1, post=self.post)

        response = self.client.post(
            reverse('like_post', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(self.post.likes.count(), 0)

    def test_like_post_redirects_to_project(self):
        self.client.login(username='testuser', password='testpass')
        self.post.project = self.project
        self.post.save()

        response = self.client.post(reverse('like_post', args=[self.post.id]), follow=True)

        self.assertRedirects(
            response,
            reverse('project', kwargs={'project_id': self.project.id})
        )


    # friend request
    def test_get_friends(self):
        FriendRequest.objects.create(from_user=self.test_user1, to_user=self.friend_user, status='accepted')
        FriendRequest.objects.create(from_user=self.student2_user, to_user=self.test_user1, status='accepted')
        FriendRequest.objects.create(from_user=self.test_user1, to_user=self.test_user2, status='declined')

        friends = get_friends(self.test_user1)
        friend_usernames = [user.username for user in friends]

        self.assertIn('frienduser', friend_usernames)
        self.assertIn('student2', friend_usernames)
        self.assertNotIn('testuser2', friend_usernames)
        self.assertEqual(len(friend_usernames), 2)

    def test_send_friend_request_already_exists(self):
        self.client.login(username='testuser', password='testpass')
        FriendRequest.objects.create(from_user=self.test_user1, to_user=self.test_user2)

        response = self.client.post(
            reverse('send_friend_request', args=[self.test_user2.id])
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"message": "Friend request already exists"})

    def test_send_friend_request_to_self(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(
            reverse('send_friend_request', args=[self.test_user1.id])
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Cannot send request to yourself"})

    def test_send_friend_request(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('send_friend_request', args=[self.test_user2.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message": "Friend request sent"})
        self.assertTrue(FriendRequest.objects.filter(
            from_user=self.test_user1,
            to_user=self.test_user2
        ).exists())

    def test_accept_friend_request(self):
        fr = FriendRequest.objects.create(
            from_user=self.test_user1,
            to_user=self.friend_user,
            status=FriendRequest.PENDING
        )
        self.client.login(username='frienduser', password='testpass')
        response = self.client.get(reverse('accept_friend_request', args=[fr.id]))
        self.assertEqual(response.status_code, 302)
        fr.refresh_from_db()
        self.assertEqual(fr.status, FriendRequest.ACCEPTED)

    def test_decline_friend_request(self):
        fr = FriendRequest.objects.create(
            from_user=self.test_user1,
            to_user=self.test_user2
        )

        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('decline_friend_request', args=[fr.id]))

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('friend_requests', kwargs={'username': 'testuser2'}))
        self.assertFalse(FriendRequest.objects.filter(id=fr.id).exists())

    def test_friend_requests_view(self):
        FriendRequest.objects.create(from_user=self.test_user1, to_user=self.test_user2)

        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('friend_requests', kwargs={'username': 'testuser2'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/friend_requests.html')

    # Share
    def test_share_post(self):
        self.client.login(username='testuser', password='testpass')
        self.assertFalse(
            Share.objects.filter(user=self.test_user1, post=self.post).exists()
        )
        response = self.client.post(reverse('share_post', args=[self.post.id]))

        self.assertRedirects(
            response,
            reverse('user_reposts', kwargs={'username': self.test_user1.username})
        )

    def test_shared_posts_list(self):
        Share.objects.create(user=self.test_user1, post=self.post)

        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_reposts', kwargs={'username': 'testuser'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/user_reposts.html')

    def test_share_post_duplicate_warning(self):
        Repost.objects.create(user=self.test_user1, original_post=self.post)

        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('share_post', args=[self.post.id]), follow=True)

        self.assertRedirects(
            response,
            reverse('user_reposts', kwargs={'username': self.test_user1.username})
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already shared this post" in str(m) for m in messages))


    # Societies
    def test_edit_society_profile_get(self):
        self.client.login(username='society1', password='pass1234')
        response = self.client.get(reverse('edit_society_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_society.html')

    def test_edit_society_profile_post(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('edit_society_profile')
        response = self.client.post(url, {
            'society_name': 'Updated Society Name',
            'contact_email': 'updated_society@example.com'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/society_profile.html')

        updated_profile = SocietyProfile.objects.get(user=self.society_user)
        self.assertEqual(updated_profile.society_name, 'Updated Society Name')
        self.assertEqual(updated_profile.contact_email, 'updated_society@example.com')

        self.assertEqual(updated_profile.user.email, 'updated_society@example.com')

        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("updated successfully" in str(m) for m in messages_list))


    def test_contact_profile_student(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contact_profile', args=[self.test_user1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context)

    def test_contact_profile_society(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contact_profile', args=[self.society_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['email'], 'society@example.com')

    # Joined Societies / Society Members
    def test_society_members_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('society_members', args=[self.society_user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('society', response.context)

    def test_student_join_society(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('society_members', args=[self.society_user.username])
        response = self.client.post(url, {'action': 'join'})
        self.assertRedirects(response, url)
        self.assertTrue(self.society_profile.members.filter(id=self.student1_profile.id).exists())

    def test_student_leave_society(self):
        self.society_profile.members.add(self.student1_profile)
        self.client.login(username='student1', password='pass1234')
        url = reverse('society_members', args=[self.society_user.username])
        response = self.client.post(url, {'action': 'leave'})
        self.assertRedirects(response, url)
        self.assertFalse(self.society_profile.members.filter(id=self.student1_profile.id).exists())

    def test_society_kick_student(self):
        self.society_profile.members.add(self.student1_profile)
        self.client.login(username='society1', password='pass1234')
        url = reverse('society_members', args=[self.society_user.username])
        response = self.client.post(url, {
            'action': 'kick',
            'student_id': self.student1_profile.id
        })
        self.assertRedirects(response, url)
        self.assertFalse(self.society_profile.members.filter(id=self.student1_profile.id).exists())


    def test_joined_societies_view(self):
        self.test_profile1.joined_societies.add(self.society_profile)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(
            reverse('joined_societies', args=[self.test_user1.username])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('societies', response.context)
        self.assertIn(self.society_profile, response.context['societies'])
