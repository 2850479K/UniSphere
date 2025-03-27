from django.test import SimpleTestCase
from django.urls import reverse, resolve
from UniSphereApp import views
from django.contrib.auth.views import LogoutView


class TestUrls(SimpleTestCase):

    def test_home_url(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home)

    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register)

    def test_create_profile_url(self):
        url = reverse('create_profile')
        self.assertEqual(resolve(url).func, views.create_profile)

    def test_edit_profile_url(self):
        url = reverse('edit_profile')
        self.assertEqual(resolve(url).func, views.edit_profile)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, views.custom_login)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_profile_url(self):
        url = reverse('profile', args=['testuser'])
        self.assertEqual(resolve(url).func, views.profile)

    def test_my_profile_url(self):
        url = reverse('my_profile')
        self.assertEqual(resolve(url).func, views.my_profile)

    def test_welcome_url(self):
        url = reverse('welcomepage')
        self.assertEqual(resolve(url).func, views.welcomepage)

    def test_about_url(self):
        url = reverse('about')
        self.assertEqual(resolve(url).func, views.about)

    def test_profile_posts_url(self):
        url = reverse('profile_posts', args=['testuser'])
        self.assertEqual(resolve(url).func, views.profile_posts)

    # Portfolio & Projects
    def test_create_project_url(self):
        url = reverse('create_project')
        self.assertEqual(resolve(url).func, views.create_project)

    def test_user_portfolio_url(self):
        url = reverse('user_portfolio', args=['testuser'])
        self.assertEqual(resolve(url).func, views.user_portfolio)

    def test_project_url(self):
        url = reverse('project', args=[1])
        self.assertEqual(resolve(url).func, views.project)

    def test_edit_project_url(self):
        url = reverse('edit_project', args=[1])
        self.assertEqual(resolve(url).func, views.edit_project)

    def test_delete_project_url(self):
        url = reverse('delete_project', args=[1])
        self.assertEqual(resolve(url).func, views.delete_project)

    # Posts
    def test_create_post_url(self):
        url = reverse('create_post', args=[1])
        self.assertEqual(resolve(url).func, views.create_post)

    def test_edit_post_url(self):
        url = reverse('edit_post', args=[1])
        self.assertEqual(resolve(url).func, views.edit_post)

    def test_delete_post_url(self):
        url = reverse('delete_post', args=[1])
        self.assertEqual(resolve(url).func, views.delete_post)

    def test_view_post_url(self):
        url = reverse('view_post', args=[1])
        self.assertEqual(resolve(url).func, views.view_post)

    def test_view_all_comments_url(self):
        url = reverse('view_all_comments', args=[1])
        self.assertEqual(resolve(url).func, views.view_all_comments)

    def test_create_profile_post_url(self):
        url = reverse('create_profile_post')
        self.assertEqual(resolve(url).func, views.create_post)

    # Society
    def test_edit_society_profile_url(self):
        url = reverse('edit_society_profile')
        self.assertEqual(resolve(url).func, views.edit_society_profile)

    def test_society_members_url(self):
        url = reverse('society_members', args=['society1'])
        self.assertEqual(resolve(url).func, views.society_members)

    def test_joined_societies_url(self):
        url = reverse('joined_societies', args=['student1'])
        self.assertEqual(resolve(url).func, views.joined_societies)

    # Search
    def test_search_users_url(self):
        url = reverse('search_users')
        self.assertEqual(resolve(url).func, views.search_users)

    def test_contact_profile_url(self):
        url = reverse('contact_profile', args=[1])
        self.assertEqual(resolve(url).func, views.contact_profile)

    # Social Features
    def test_share_post_url(self):
        url = reverse('share_post', args=[1])
        self.assertEqual(resolve(url).func, views.share_post)

    def test_add_comment_url(self):
        url = reverse('add_comment', args=[1])
        self.assertEqual(resolve(url).func, views.add_comment)

    def test_get_comments_url(self):
        url = reverse('get_comments', args=[1])
        self.assertEqual(resolve(url).func, views.get_comments)

    def test_shared_posts_list_url(self):
        url = reverse('shared_posts_list')
        self.assertEqual(resolve(url).func, views.shared_posts_list)

    def test_like_post_url(self):
        url = reverse('like_post', args=[1])
        self.assertEqual(resolve(url).func, views.like_post)

    # Friend Requests
    def test_send_friend_request_url(self):
        url = reverse('send_friend_request', args=[1])
        self.assertEqual(resolve(url).func, views.send_friend_request)

    def test_accept_friend_request_url(self):
        url = reverse('accept_friend_request', args=[1])
        self.assertEqual(resolve(url).func, views.accept_friend_request)

    def test_decline_friend_request_url(self):
        url = reverse('decline_friend_request', args=[1])
        self.assertEqual(resolve(url).func, views.decline_friend_request)

    def test_friend_requests_url(self):
        url = reverse('friend_requests')
        self.assertEqual(resolve(url).func, views.friend_requests)

    def test_remove_friend_url(self):
        url = reverse('remove_friend', args=[1])
        self.assertEqual(resolve(url).func, views.remove_friend)
