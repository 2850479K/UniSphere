from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = 'UniSphereApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('portfolio/', views.post_list, name='post_list'),
    path('portfolio/createpost/', views.create_post, name='create_post'),
    path('portfolio/viewpost/<int:project_id>/', views.view_post, name='view_post'),
    path('portfolio/editpost/<int:project_id>/', views.edit_post, name='edit_post'),
    path('portfolio/deletepost/<int:project_id>/', views.delete_post, name='delete_post'),
    path('recruiter/create-profile/', views.create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', views.search_students, name='search_students'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
