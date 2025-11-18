"""
URL configuration for yoto_local project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from api import views as api_views

urlpatterns = [
    path('', api_views.app_page, name='app_page'),
    path('sw.js', api_views.service_worker, name='service_worker'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('callback', api_views.oauth_callback, name='oauth_callback'),
]

# Only include setup and callback routes if not using env credentials
if not settings.USE_ENV_CREDENTIALS:
    urlpatterns.insert(1, path('setup/', api_views.setup_page, name='setup_page'))
    
else:
    urlpatterns.insert(1, path('setup/', api_views.setup_account_only_page, name='setup_account_only_page'))