from django.urls import path
from django.contrib.auth import views as auth_views
from UniSphereApp import views
from .views import create_recruiter_profile
from .views import search_students

urlpatterns = [
    #home page
    path('', views.home, name='home'),
    #user authentication
    path('register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('accounts/logout/', auth_views.LoginView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),
    #portfolio URLs
    path('portfolio/', views.post_list, name='post_list'),  # View all projects
    path('portfolio/createpost/', views.create_post, name='create_post'),  # Create a new project
    path('portfolio/viewpost/<int:project_id>/', views.view_post, name='view_post'),  # View & edit project
    path('portfolio/editpost/<int:project_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:project_id>/', views.delete_post, name='delete_post'),
    path('recruiter/create-profile/', create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', search_students, name='search_students'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('like/<int:portfolio_id>/', views.like_portfolio, name='like_portfolio'),
    path('comment/<int:portfolio_id>/', views.comment_on_portfolio, name='comment_on_portfolio'),
    path('share/<int:portfolio_id>/', views.share_portfolio, name='share_portfolio'),
]