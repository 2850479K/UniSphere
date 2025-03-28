from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.urls import re_path
from UniSphereApp import views



urlpatterns = [
    path('', views.welcomepage, name='welcomepage'),
    path('admin/', admin.site.urls),
    path('', include('UniSphereApp.urls')),
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='UniSphereApp/login.html'), name='login'),



    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
