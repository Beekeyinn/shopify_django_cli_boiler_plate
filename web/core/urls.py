"""
URL configuration for core project.

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
from django.urls import path

from home.views import HomeView
from accounts.views.shopify import UpdateAPPView
from accounts.views.shopify import callback
from accounts.views.shopify import uninstall

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="root_path"),
    path("api/auth/callback", callback, name="callback"),
    path("api/auth/", UpdateAPPView.as_view(), name="update"),
    path("api/webhooks", uninstall, name="uninstall"),
]
