from django.urls import path

from .views import image_to_text

urlpatterns = [
    path("", image_to_text),
]
