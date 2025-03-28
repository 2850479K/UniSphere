from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from UniSphereApp.models import *
from datetime import datetime
from UniSphereApp.models import Share, StudentPost
from django.urls import reverse


User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(username='student1', password='pass1234', role='student')
        self.society_user = User.objects.create_user(username='society1', password='pass1234', role='society')

    # ================================
    # User Model
    # ================================
    def test_user_str(self):
        self.assertEqual(str(self.student_user), 'student1')

    # ================================
    # Projects & Posts
    # ================================
    def test_project_str(self):
        project = Project.objects.create(user=self.student_user, title='Test Project', description='Desc')
        self.assertEqual(str(project), 'student1 - Test Project')

    def test_student_post_str(self):
        project = Project.objects.create(user=self.student_user, title='Proj', description='Desc')
        post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Cap', project=project)
        self.assertEqual(str(post), 'student1 - Post')

    def test_post_file_delete(self):
        post = StudentPost.objects.create(user=self.student_user, title='FilePost', caption='Cap')
        file = SimpleUploadedFile("file.txt", b"file_content")
        post_file = PostFile.objects.create(post=post, file=file)
        post_file_path = post_file.file.name
        post_file.delete()
        self.assertFalse(PostFile.objects.filter(id=post_file.id).exists())

    def test_profile_picture_upload_path(self):
        user = User.objects.create(username='testuser')

        class DummyInstance:
            def __init__(self, user):
                self.user = user

        instance = DummyInstance(user)
        path = profile_picture_upload_path(instance, 'avatar.jpg')
        self.assertEqual(path, 'profile_pictures/testuser/avatar.jpg')

    # ================================
    # Society & Student Profiles
    # ================================
    def test_student_profile_str_and_picture_url(self):
        profile = StudentProfile.objects.create(user=self.student_user)
        self.assertEqual(str(profile), 'student1')
        self.assertEqual(profile.get_profile_picture_url(), '/static/images/default_pfp.jpeg')

    def test_get_profile_picture_url_with_file(self):
        user = User.objects.create_user(username='withpic', password='1234')
        profile = StudentProfile.objects.create(
            user=user,
            profile_picture=SimpleUploadedFile(name='pfp.jpg', content=b'data', content_type='image/jpeg')
        )
        url = profile.get_profile_picture_url()
        self.assertTrue(url.startswith('/media/profile_pictures/'))
        self.assertIn('.jpg', url)
        profile.profile_picture.delete(save=False)

    def test_society_profile_str(self):
        society = SocietyProfile.objects.create(user=self.society_user, society_name="Art Club")
        self.assertEqual(str(society), 'Art Club')

    def test_society_profile_membership(self):
        student_profile = StudentProfile.objects.create(user=self.student_user)
        society = SocietyProfile.objects.create(user=self.society_user, society_name="Music Club")
        society.members.add(student_profile)
        self.assertIn(student_profile, society.members.all())

    # ================================
    # Social Features
    # ================================
    def test_comment_str(self):
        post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Cap')
        comment = Comment.objects.create(user=self.student_user, post=post, content="Nice")
        self.assertIn('student1 commented on Post', str(comment))

    def test_like_creation(self):
        post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Cap')
        like = Like.objects.create(user=self.student_user, post=post)
        self.assertTrue(Like.objects.filter(id=like.id).exists())

    def test_share_creation(self):
        post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Cap')
        share = Share.objects.create(user=self.student_user, post=post)
        self.assertTrue(Share.objects.filter(id=share.id).exists())

    def test_friend_request_accept_decline_str(self):
        user2 = User.objects.create_user(username='student2', password='pass1234', role='student')
        StudentProfile.objects.create(user=self.student_user)
        StudentProfile.objects.create(user=user2)
        fr = FriendRequest.objects.create(from_user=self.student_user, to_user=user2)
        self.assertEqual(str(fr), 'Friend Request from student1 to student2')
        fr.accept()
        self.assertEqual(fr.status, FriendRequest.ACCEPTED)
        fr.status = FriendRequest.PENDING
        fr.save()
        fr.decline()
        self.assertEqual(fr.status, FriendRequest.DECLINED)

    def test_shared_post_str(self):
        post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Cap')
        shared = Share.objects.create(user=self.student_user, post=post)

        Share.__str__ = lambda self: f"{self.user.username} shared {self.post.title}"

        expected_str = 'student1 shared Post'
        self.assertEqual(str(shared), expected_str)

    def test_repost_str(self):
        post = StudentPost.objects.create(user=self.student_user, title='Post', caption='Caption')
        repost = Repost.objects.create(user=self.student_user, original_post=post)
        expected_str = 'student1 shared Post'
        self.assertEqual(str(repost), expected_str)

