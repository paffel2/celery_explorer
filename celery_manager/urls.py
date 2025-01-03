"""
URL configuration for celery_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from celery_explorer.views import task_index


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/task_maker/", include("task_creator.urls")),
    path("celery_explorer/", include("src.celery_explorer.urls")),
    # path("celery_explorer/", task_index, name="explorer"),
]