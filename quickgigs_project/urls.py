"""
URL configuration for todo_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),                    # Homepage and site-wide pages
    path('accounts/', include('accounts.urls')),       # User management
    path('gigs/', include('gigs.urls')),              # Job board functionality
    path('payments/', include('payments.urls')),       # Payment processing
]

# Temporarily disabled for testing screenshots
# if settings.DEBUG:
#     # urlpatterns = [
#     #     path('__debug__/', include(debug_toolbar.urls)),
#     # ] + urlpatterns