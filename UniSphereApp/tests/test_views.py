from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth import get_user_model
from UniSphereApp.models import User, StudentProfile, StudentPost, Project, PostFile, SocietyProfile

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.student_user = User.objects.create_user(username='student1', password='pass1234', role='student')
        self.society_user = User.objects.create_user(username='society1', password='pass1234', role='society')  

        self.student_profile = StudentProfile.objects.create(user=self.student_user)
        self.society_profile = SocietyProfile.objects.create(user=self.society_user, society_name='Soc Club')

        self.project = Project.objects.create(user=self.student_user, title='Test Project', description='Desc')
        self.post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Cap',
                                               project=self.project)

    # General Views
    def test_home_redirect_for_anonymous(self):
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

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'invalid'})
        self.assertEqual(response.status_code, 200)

    #Profile
    def test_profile_posts_view(self):
        StudentPost.objects.create(user=self.student_user, title='Post 1', caption='Caption')
        url = reverse('profile_posts', kwargs={'username': self.student_user.username})
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
        self.assertTrue(StudentProfile.objects.filter(user=self.student_user).exists())

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
            'society_name': 'New Society'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SocietyProfile.objects.filter(user=self.society_user).exists())

    def test_profile_view_as_owner_student(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': 'student1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/student_profile.html')

    def test_profile_view_as_other_student_private(self):
        user2 = User.objects.create_user(username='student2', password='pass1234', role='student')
        profile2 = StudentProfile.objects.create(user=user2, full_name='Other', visibility='private')
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': 'student2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/private_profile.html')

    def test_profile_view_society(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': 'society1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/society_profile.html')

    def test_society_profile_view_get(self):
        self.client.login(username='society1', password='pass1234')
        url = reverse('profile', kwargs={'username': 'society1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/society_profile.html')
        self.assertIn('is_member', response.context)
        self.assertFalse(response.context['is_member'])

    def test_society_profile_join_post(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': 'society1'})
        response = self.client.post(url, {'action': 'join'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.society_profile.members.filter(id=self.student_profile.id).exists())

    def test_society_profile_leave_post(self):
        self.society_profile.members.add(self.student_profile)
        self.client.login(username='student1', password='pass1234')
        url = reverse('profile', kwargs={'username': 'society1'})
        response = self.client.post(url, {'action': 'leave'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.society_profile.members.filter(id=self.student_profile.id).exists())

    def test_remove_friend_post(self):
        self.student_profile.friends.add(self.student2_profile)
        self.student2_profile.friends.add(self.student_profile)

        self.client.login(username='student1', password='pass1234')
        url = reverse('remove_friend', kwargs={'user_id': self.student2.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message": f"Removed friend {self.student2.username}."})
        self.assertFalse(self.student_profile.friends.filter(id=self.student2_profile.id).exists())
        self.assertFalse(self.student2_profile.friends.filter(id=self.student_profile.id).exists())

    def test_remove_friend_invalid_method(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('remove_friend', kwargs={'user_id': self.student2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "Invalid request method."})

    def test_my_profile_redirect(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.get(reverse('my_profile'))
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'student1'}))

    def test_edit_profile_get(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('edit_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_profile.html')
        self.assertIn('form', response.context)

    def test_edit_profile_post(self):
        self.client.login(username='student1', password='pass1234')
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
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'student1'}))
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.full_name, 'New Name')

    #Portfolios & Projects
    def test_user_portfolio_view(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('user_portfolio', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/portfolio.html')
        self.assertIn('projects', response.context)
        self.assertIn(self.project, response.context['projects'])

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
        self.assertTrue(Project.objects.filter(title='New Project').exists())

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
        response = self.client.post(url, {'title': 'Hacked', 'description': 'X'})
        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))
        self.project.refresh_from_db()
        self.assertNotEqual(self.project.title, 'Hacked')

    def test_delete_project_post(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('delete_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('user_portfolio', kwargs={'username': self.user.username}))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_get_redirect(self):
        self.client.login(username='student1', password='pass1234')
        url = reverse('delete_project', kwargs={'project_id': self.project.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('project', kwargs={'project_id': self.project.id}))

    #Posts
    def test_create_post_get(self):
        response = self.client.get(reverse('create_post', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_post_post_valid(self):
        file = SimpleUploadedFile("file.txt", b"file_content")
        response = self.client.post(
            reverse('create_post', args=[self.project.id]),
            data={'title': 'New Post', 'caption': 'New Cap', 'files': file},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(StudentPost.objects.filter(title='New Post').exists())

    def test_edit_post_get(self):
        response = self.client.get(reverse('edit_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_edit_post_post_valid(self):
        response = self.client.post(
            reverse('edit_post', args=[self.post.id]),
            data={'title': 'Updated Title', 'caption': 'Cap'}
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_delete_post_post(self):
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('project', args=[self.project.id]))
        self.assertFalse(StudentPost.objects.filter(id=self.post.id).exists())

    def test_view_post(self):
        response = self.client.get(reverse('view_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_search_users_empty(self):
        response = self.client.get(reverse('search_users'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_results'])

    def test_search_users_student_match(self):
        self.profile.interests = "Django"
        self.profile.save()
        response = self.client.get(reverse('search_users'), {'interests': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_results'])
        self.assertIn(self.profile, response.context['students'])

    # Social Features
    def test_get_comments(self):
        Comment.objects.create(user=self.user, post=self.post, content='Great!')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('get_comments', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.json())

    def test_like_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('like_post', args=[self.post.id]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])

    def test_add_comment(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_comment', args=[self.post.id]), {'content': 'Nice post!'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(post=self.post).exists())

    def test_view_all_comments(self):
        Comment.objects.create(user=self.user, post=self.post, content='Another comment')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('view_all_comments', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/all_comments.html')

    def test_send_friend_request(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('send_friend_request', args=[self.user2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user, to_user=self.user2).exists())

    def test_accept_friend_request(self):
        fr = FriendRequest.objects.create(from_user=self.user, to_user=self.user2)
        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('accept_friend_request', args=[fr.id]))
        self.assertEqual(response.status_code, 302)
        fr.refresh_from_db()
        self.assertEqual(fr.status, FriendRequest.ACCEPTED)

    def test_decline_friend_request(self):
        fr = FriendRequest.objects.create(from_user=self.user, to_user=self.user2)
        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('decline_friend_request', args=[fr.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FriendRequest.objects.filter(id=fr.id).exists())

    def test_friend_requests_view(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.user2)
        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('friend_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/friend_requests.html')

    def test_share_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('share_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('shared_posts_list'))
        self.assertTrue(SharedPost.objects.filter(user=self.user, original_post=self.post).exists())

    def test_shared_posts_list(self):
        SharedPost.objects.create(user=self.user, original_post=self.post)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('shared_posts_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/shared_posts.html')

    def test_edit_society_profile_get(self):
        society = SocietyProfile.objects.create(user=self.society_user, society_name='Test Club')
        self.client.login(username='societyuser', password='testpass3')
        response = self.client.get(reverse('edit_society_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UniSphereApp/edit_society.html')

    def test_contact_profile_student(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contact_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context)

    def test_contact_profile_society(self):
        society = SocietyProfile.objects.create(user=self.society_user, society_name='Test Club',
                                                contact_email='test@society.com')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contact_profile', args=[self.society_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['email'], 'test@society.com')

    def test_society_members_view(self):
        society = SocietyProfile.objects.create(user=self.society_user, society_name='Tech Club')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('society_members', args=[self.society_user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('society', response.context)

    def test_joined_societies_view(self):
        society = SocietyProfile.objects.create(user=self.society_user, society_name='Film Club')
        self.student_profile.joined_societies.add(society)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('joined_societies', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('societies', response.context)
