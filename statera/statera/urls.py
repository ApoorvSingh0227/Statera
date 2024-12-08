"""
URL configuration for statera project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('statera.urls')),  # Include app-level URLs
]

urlpatterns = [
    path('', views.login, name='login'),                 # Login page (home.html)
    path('register/', views.register, name='register'),  # Register page
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
    path('task-info/<int:task_id>/', views.task_info, name='task_info'),
    path('project-main/<int:project_id>/', views.project_main, name='project_main'),
    path('employee-info/<int:employee_id>/', views.employee_info, name='employee_info'),
    path('update-information/', views.update_information, name='update_information'),

]