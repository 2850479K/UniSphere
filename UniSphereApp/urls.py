from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import recruiter_dashboard
from .views import invite_student, save_student
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),

    #portfolio URLs
    path('portfolio/', views.post_list, name='post_list'),  # View all projects
    path('portfolio/createpost/', views.create_post, name='create_post'),  # Create a new project
    path('portfolio/viewpost/<int:project_id>/', views.view_post, name='view_post'),  # View & edit project
    path('portfolio/editpost/<int:project_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:project_id>/', views.delete_post, name='delete_post'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/', views.my_profile, name='my_profile'),

    # Portfolio & Projects
    path('portfolio/create_project/', views.create_project, name='create_project'),
    path('portfolio/<str:username>/', views.user_portfolio, name='user_portfolio'),
    path('project/<int:project_id>/', views.project, name='project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    # Posts
    path('project/<int:project_id>/createpost/', views.create_post, name='create_post'),
    path('portfolio/viewpost/<int:post_id>/', views.view_post, name='view_post'),
    path('portfolio/editpost/<int:post_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:post_id>/', views.delete_post, name='delete_post'),

    # Recruiter & Student Search
    path('recruiter/create-profile/', create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', search_students, name='search_students'),
    path("recruiter/dashboard/", recruiter_dashboard, name="recruiter_dashboard"),
    path('recruiter/invite/<int:student_id>/', invite_student, name='invite_student'),
    path('recruiter/save/<int:student_id>/', save_student, name='save_student'),
]


