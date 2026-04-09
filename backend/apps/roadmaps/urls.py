from django.urls import path

from .views import roadmaps_collection, roadmaps_detail

urlpatterns = [
    path("", roadmaps_collection),
    path("<uuid:roadmap_id>", roadmaps_detail),
]
