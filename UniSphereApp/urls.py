from django.urls import path
from UniSphereApp import views
from .views import create_recruiter_profile
from .views import search_students


urlpatterns = [
    path('recruiter/create-profile/', create_recruiter_profile, name='create_recruiter_profile'),
    path('recruiter/search-students/', search_students, name='search_students'),
]
