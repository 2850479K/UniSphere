from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', LogoutView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/', views.my_profile, name='my_profile'),
    
    # Portfolio & Projects
    path('portfolio/', views.post_list, name='post_list'),  # View all projects
    path('portfolio/createpost/', views.create_post, name='create_post'),  # Create a new project
    path('portfolio/viewpost/<int:post_id>/', views.view_post, name='view_post'),  # View & edit project
    path('portfolio/editpost/<int:post_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:post_id>/', views.delete_post, name='delete_post'),
    path('portfolio/create_project/', views.create_project, name='create_project'),
    path('portfolio/<str:username>/', views.user_portfolio, name='user_portfolio'),
    path('project/<int:project_id>/', views.project, name='project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    
    # Recruiter & Student Search
    path('recruiter/create-profile/', views.create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', views.search_students, name='search_students'),
    path('search_students/', views.search_students, name='search_students'),
    
    # Social Features
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:post_id>/share/', views.share_post, name='share_post'),
    
    path('friend-request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('shared-posts/', views.shared_posts_list, name='shared_posts_list'),
]
