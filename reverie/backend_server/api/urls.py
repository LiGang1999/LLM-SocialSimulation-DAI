"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from api import control
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("start/", control.start, name="start"),
    path("command/", control.add_command, name="add_command"),
    path("list_envs/", control.list_envs, name="list_envs"),
    path("persona/", control.get_persona, name="persona"),
    path("env_info/", control.get_env_info, name="env_info"),
    path("publish_event/", control.publish_event, name="publish_event"),
    path("run/", control.run, name="run"),
]
