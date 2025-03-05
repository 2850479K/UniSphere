from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('logout/', auth_views.LoginView.as_view(template_name='UniSphereApp/logout.html'), name='logout'),
]