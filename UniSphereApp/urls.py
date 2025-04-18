from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .views import welcomepage

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', LogoutView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/', views.my_profile, name='my_profile'),
    path('welcome/', views.welcomepage, name='welcomepage'),
    path('about/', views.about, name='about'),
    path('profile/<str:username>/posts/', views.profile_posts, name='profile_posts'),

    # Portfolio & Projects
    path('portfolio/create_project/', views.create_project, name='create_project'),
    path('portfolio/<str:username>/', views.user_portfolio, name='user_portfolio'),
    path('project/<int:project_id>/', views.project, name='project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    # Posts
    path('project/<int:project_id>/createpost/', views.create_post, name='create_post'),
    path('portfolio/editpost/<int:post_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/comments/all/', views.view_all_comments, name='view_all_comments'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('create_profile_post/', views.create_post, name='create_profile_post'),


    #Society    
    path('edit-society-profile/', views.edit_society_profile, name='edit_society_profile'),
    path('society/<str:society_username>/members/', views.society_members, name='society_members'),
    path('student/<str:username>/joined-societies/', views.joined_societies, name='joined_societies'),

    #Search
    path('search-users/', views.search_users, name='search_users'),
    path('contact/<int:user_id>/', views.contact_profile, name='contact_profile'),
    
    # Social Features
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('post/<int:post_id>/share/', views.share_post, name='share_post'),
    path('profile/<str:username>/reposts/', views.user_reposts, name='user_reposts'),
    path("like-post/<int:post_id>/", views.like_post, name="like_post"),

    # Friend Requests
    path('friend-request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/<str:username>/', views.student_friends_and_requests, name='friend_requests'), 
    path('remove_friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
]
