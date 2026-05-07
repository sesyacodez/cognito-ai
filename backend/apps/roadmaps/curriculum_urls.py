from django.urls import path

from .views import (
    curriculum_course_expand,
    curriculums_collection,
    curriculums_detail,
)

urlpatterns = [
    path("", curriculums_collection),
    path("<uuid:curriculum_id>", curriculums_detail),
    path(
        "<uuid:curriculum_id>/courses/<uuid:course_id>/expand",
        curriculum_course_expand,
    ),
]
