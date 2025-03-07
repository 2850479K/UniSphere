from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/', views.post_list, name='post_list'),  # View all projects
    path('portfolio/add-project/', views.create_post, name='create_post'),  # Create a new project
    path('portfolio/view-project/<int:project_id>/', views.view_post, name='view_post'),  # View & edit project
]
