from typing import List

from django.urls import URLPattern, path

from . import views

app_name: str = "pages"

urlpatterns: List[URLPattern] = [
    path("about/", views.AboutTemplateView.as_view(), name="about"),
    path("rules/", views.RulesTemplateView.as_view(), name="rules"),
]
