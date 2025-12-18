"""
URL configuration for job_portal project.

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
from django.conf.urls.static import static
from debug_token_view import DebugTokenAPI
from test_endpoint import TestJobsAPI
from token_debug import TokenDebugAPI
from simple_auth import SimpleLoginAPI
from simple_profile import SimpleProfileAPI
from header_debug import HeaderDebugAPI
from open_test import OpenTestAPI
from stats_view import StatsAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('profile/', include('profile_app.urls')),
    path('jobs/', include('job_postings.urls')),
    path('relationships/', include('relationships.urls')),
    path('feeds/', include('feeds.urls')),
    path('debug-token/', DebugTokenAPI.as_view(), name='debug-token'),
    path('test-jobs/', TestJobsAPI.as_view(), name='test-jobs'),
    path('token-debug/', TokenDebugAPI.as_view(), name='token-debug'),
    path('simple-login/', SimpleLoginAPI.as_view(), name='simple-login'),
    path('simple-profile/', SimpleProfileAPI.as_view(), name='simple-profile'),
    path('debug-headers/', HeaderDebugAPI.as_view(), name='debug-headers'),
    path('open-test/', OpenTestAPI.as_view(), name='open-test'),
    path('stats/', StatsAPI.as_view(), name='stats'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)