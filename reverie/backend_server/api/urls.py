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

from api import controls, views
from django.contrib import admin
from django.urls import path, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("start/", controls.start, name="start"),
    path("command/", controls.add_command, name="add_command"),
    path("fetch_templates/", controls.fetch_templates, name="fetch_templates"),
    path("persona/", controls.get_persona, name="persona"),
    path("personas_info/", controls.personas_info, name="personas_info"),
    path("persona_detail/", controls.persona_detail, name="persona_detail"),
    path("fetch_template/", controls.fetch_template, name="fetch_template"),
    path("publish_event/", controls.publish_event, name="publish_event"),
    path("status/", controls.query_status, name="query_status"),
    path("chat/", controls.chat, name="chat"),
    path("run/", controls.run, name="run"),
    #
    # The following are migrated from the original frontend server
    #
    path("", views.landing, name="landing"),
    path("simulator_home", views.home, name="home"),
    re_path(
        r"^demo/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<play_speed>[\w-]+)/$",
        views.demo,
        name="demo",
    ),
    re_path(r"^replay/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/$", views.replay, name="replay"),
    re_path(
        r"^replay_persona_state/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<persona_name>[\w-]+)/$",
        views.replay_persona_state,
        name="replay_persona_state",
    ),
    path("process_environment/", views.process_environment, name="process_environment"),
    path("update_environment/", views.update_environment, name="update_environment"),
    path("path_tester/", views.path_tester, name="path_tester"),
    path("path_tester_update/", views.path_tester_update, name="path_tester_update"),
]
