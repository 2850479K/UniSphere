from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from UniSphereApp import views
from .views import create_recruiter_profile
from .views import search_students
from django.contrib.auth.views import LogoutView


urlpatterns = [
    #home page
    path('', views.home, name='home'),
    #user authentication
    path('register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    #portfolio URLs
    path('portfolio/<str:username>/', views.user_portfolio, name='user_portfolio'),
    path('portfolio/create_project/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/createpost/', views.create_post, name='create_post'),
    path('portfolio/viewpost/<int:project_id>/', views.view_post, name='view_post'),
    path('portfolio/editpost/<int:project_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:project_id>/', views.delete_post, name='delete_post'),
]

