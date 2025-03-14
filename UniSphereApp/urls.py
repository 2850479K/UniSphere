from django.urls import path,include
from . import views
from .views import (
    home, register, post_list, create_post, view_post,
    edit_post, delete_post, create_recruiter_profile,
    search_students, profile, edit_profile, logout_view
)
from django.contrib.auth import views as auth_views
from UniSphereApp import views
from .views import create_recruiter_profile
from .views import search_students
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import MyLogoutView

urlpatterns = [
    path('',views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),

    path('portfolio/', views.post_list, name='post_list'),
    path('portfolio/createpost/', views.create_post, name='create_post'),
    path('portfolio/viewpost/<int:project_id>/', views.view_post, name='view_post'),
    path('portfolio/editpost/<int:project_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:project_id>/', views.delete_post, name='delete_post'),

    path('recruiter/create-profile/', create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', search_students, name='search_students'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]

