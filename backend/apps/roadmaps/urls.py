from django.urls import path

from .views import roadmaps_collection

urlpatterns = [
    path("", roadmaps_collection),
]
