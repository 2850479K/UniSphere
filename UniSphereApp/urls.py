from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
]

