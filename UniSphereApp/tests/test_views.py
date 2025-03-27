from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth import get_user_model
from UniSphereApp.forms import ProjectForm
from django.contrib.messages import get_messages
from UniSphereApp.models import User, StudentProfile, StudentPost, Project, PostFile, SocietyProfile, Comment, SharedPost, Comment, FriendRequest
import shutil
import os
from django.conf import settings

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
        self.student1_profile = StudentProfile.objects.create(user=self.student1_user)

        # society1
        self.society_user = User.objects.create_user(
            username='society1',
            password='pass1234',
            role='society'
        )
        self.society_profile = SocietyProfile.objects.create(
            user=self.society_user,
            society_name='Test Society',
            contact_email='society@example.com'
        )

        # 登录 student1
        self.client.login(username='student1', password='pass1234')

        # 一个项目和帖子，属于 student1
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

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'wrong',
            'password': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid username or password" in str(m) for m in messages))

    def test_profile_posts_view(self):
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

    def test_create_profile_student(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/create_profile.html')


    def test_create_profile_student_post(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.post(url, {
            'full_name': 'New Name',
            'gender': 'male'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudentProfile.objects.filter(user=self.student1_user).exists())

    def test_create_profile_society(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/create_profile.html')


    def test_create_profile_society_post(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('create_profile')
        response = self.client.post(url, {
            'society_name': 'New Society',
            'contact_email': 'new@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SocietyProfile.objects.filter(user=self.society_user).exists())

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

    def test_remove_friend_post(self):
        self.student1_profile.friends.add(self.student2_profile)
        self.student2_profile.friends.add(self.student1_profile)

        self.client.login(username='student1', password='pass1234')
        url = reverse('remove_friend', kwargs={'user_id': self.student2_user.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('friend_requests'))

        self.student1_profile.refresh_from_db()
        self.student2_profile.refresh_from_db()

        self.assertFalse(self.student1_profile.friends.filter(id=self.student2_profile.id).exists())
        self.assertFalse(self.student2_profile.friends.filter(id=self.student1_profile.id).exists())

    def test_remove_friend_invalid_method(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('remove_friend', kwargs={'user_id': self.student2_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('friend_requests'))

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

    def test_delete_post_post(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('project', args=[self.project.id]))
        self.assertFalse(StudentPost.objects.filter(id=self.post.id).exists())

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


    # friend request
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
        self.assertRedirects(response, reverse('friend_requests'))
        self.assertFalse(FriendRequest.objects.filter(id=fr.id).exists())

    def test_friend_requests_view(self):
        FriendRequest.objects.create(from_user=self.test_user1, to_user=self.test_user2)
        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('friend_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/friend_requests.html')

    # Share
    def test_share_post(self):
        self.client.login(username='testuser', password='testpass')
        self.assertFalse(
            SharedPost.objects.filter(user=self.test_user1, original_post=self.post).exists()
        )
        response = self.client.post(reverse('share_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('shared_posts_list'))
        self.assertTrue(
            SharedPost.objects.filter(user=self.test_user1, original_post=self.post).exists()
        )

    def test_shared_posts_list(self):
        SharedPost.objects.create(user=self.test_user1, original_post=self.post)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('shared_posts_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/shared_posts.html')

    # Societies
    def test_edit_society_profile_get(self):
        self.client.login(username='society1', password='pass1234')
        response = self.client.get(reverse('edit_society_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_society.html')

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

    def test_joined_societies_view(self):
        self.test_profile1.joined_societies.add(self.society_profile)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(
            reverse('joined_societies', args=[self.test_user1.username])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('societies', response.context)
        self.assertIn(self.society_profile, response.context['societies'])
