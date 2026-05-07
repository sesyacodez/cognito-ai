"""
Dashboard view — GET /api/dashboard.

Returns aggregated progress summaries, XP totals, streak info, and recent activity
from the actual database models (LessonState, Roadmap).
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from apps.dashboard.services import build_dashboard_payload, get_authenticated_user


@require_GET
def dashboard(request):
    """
    GET /api/dashboard

    Returns lesson counts, streak info, recent activity, and active roadmaps
    for the authenticated user.
    """
    user = get_authenticated_user(request)
    if user is None:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    payload = build_dashboard_payload(user)

    summary = payload["summary"]
    streak = payload["streak"]

    recent_activity = []
    for lesson in payload.get("lessons", []):
        if lesson["status"] == "not_started":
            continue
        recent_activity.append({
            "lesson_id": lesson["lesson_id"],
            "lesson_title": lesson["title"],
            "status": lesson["status"],
            "xp_earned": lesson["xp_earned"],
            "stars_earned": lesson["stars_remaining"],
            "updated_at": lesson["updated_at"],
        })
    recent_activity.sort(key=lambda a: a["updated_at"], reverse=True)
    recent_activity = recent_activity[:10]

    completed_lesson_keys = {
        ls["lesson_id"]
        for ls in payload.get("lessons", [])
        if ls["status"] == "completed"
    }

    def _completed_modules(roadmap_id: str, modules: list) -> int:
        return sum(
            1 for m in modules
            if f"{roadmap_id}-{m.get('index', '')}" in completed_lesson_keys
        )

    roadmaps = []
    for rm in payload.get("roadmaps", []):
        modules = rm.get("modules", [])
        roadmap_id = rm.get("roadmap_id") or rm.get("id", "")
        roadmaps.append({
            "id": roadmap_id,
            "kind": "roadmap",
            "topic": rm.get("topic", ""),
            "mode": rm.get("mode", "learn"),
            "module_count": len(modules),
            "completed_modules": _completed_modules(roadmap_id, modules),
            "created_at": rm.get("created_at") or rm.get("createdAt", ""),
        })

    curriculums = []
    for curr in payload.get("curriculums", []):
        courses = curr.get("courses", [])
        course_count = len(courses)
        completed_courses = 0
        total_modules = 0
        completed_modules = 0
        for course in courses:
            roadmap_id = course.get("roadmap_id")
            if not roadmap_id:
                continue
            modules_for_course: list = []
            total_modules_for_course = course.get("module_count")
            if isinstance(total_modules_for_course, int):
                total_modules += total_modules_for_course
            else:
                total_modules += len(modules_for_course)
            module_completed = course.get("completed_modules") or 0
            completed_modules += module_completed
            if (
                isinstance(total_modules_for_course, int)
                and total_modules_for_course > 0
                and module_completed == total_modules_for_course
            ):
                completed_courses += 1

        curriculums.append({
            "id": curr.get("curriculum_id") or curr.get("id", ""),
            "kind": "curriculum",
            "topic": curr.get("topic", ""),
            "mode": curr.get("mode", "learn"),
            "course_count": course_count,
            "completed_courses": completed_courses,
            "module_count": total_modules,
            "completed_modules": completed_modules,
            "created_at": curr.get("created_at") or curr.get("createdAt", ""),
        })

    return JsonResponse({
        "total_xp": summary["xp_earned"],
        "total_stars": summary["stars_remaining"],
        "lessons_completed": summary["completed_lessons"],
        "lessons_in_progress": summary["in_progress_lessons"],
        "current_streak": streak["current"],
        "longest_streak": streak["longest"],
        "recent_activity": recent_activity,
        "roadmaps": roadmaps,
        "curriculums": curriculums,
        "user_name": user.name,
    })
