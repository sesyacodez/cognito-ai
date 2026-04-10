from django.urls import path

from .views import lesson_answer, lesson_delete, lesson_detail, lesson_hint, lesson_reset

urlpatterns = [
    path("<str:lesson_id>", lesson_detail),
    path("<str:lesson_id>/answer", lesson_answer),
    path("<str:lesson_id>/hint", lesson_hint),
    path("<str:lesson_id>/reset", lesson_reset),
    path("<str:lesson_id>/state", lesson_delete),
]
