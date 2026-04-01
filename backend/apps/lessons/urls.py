from django.urls import path

from .views import lesson_detail, lesson_answer, lesson_hint

urlpatterns = [
    path("<str:lesson_id>", lesson_detail),
    path("<str:lesson_id>/answer", lesson_answer),
    path("<str:lesson_id>/hint", lesson_hint),
]
