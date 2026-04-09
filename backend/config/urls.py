from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth", include("apps.auth.urls")),
    path("api/auth/", include("apps.auth.urls")),
    path("api/roadmaps", include("apps.roadmaps.urls")),
    path("api/roadmaps/", include("apps.roadmaps.urls")),
    path("api/dashboard", include("apps.dashboard.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/lessons/", include("apps.lessons.urls")),
    path("api/dashboard", include("apps.dashboard.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
]
