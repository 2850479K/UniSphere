from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from UniSphereApp import views
from .views import create_recruiter_profile
from .views import search_students

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('logout/', auth_views.LoginView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),
    path('portfolio/', views.post_list, name='post_list'),  # View all projects
    path('portfolio/add-project/', views.create_post, name='create_post'),  # Create a new project
    path('portfolio/view-project/<int:project_id>/', views.view_post, name='view_post'),  # View & edit project
    path('recruiter/create-profile/', create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', search_students, name='search_students'),
]

