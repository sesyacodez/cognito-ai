import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.roadmaps.curriculum_services import (
    create_curriculum_for_user,
    expand_course,
    get_course_for_user,
    get_curriculum_for_user,
    list_curriculums_for_user,
    plan_curriculum,
    serialize_curriculum,
    serialize_curriculum_with_first_roadmap,
)
from apps.roadmaps.services import (
    _get_module_progress_map,
    create_roadmap_for_user,
    get_authenticated_user,
    get_roadmap_for_user,
    list_roadmaps_for_user,
    normalize_mode,
    serialize_roadmap,
)
from utils.roadmap_complexity import is_broad_topic


def _auth_error() -> JsonResponse:
    return JsonResponse({"detail": "Authentication required."}, status=401)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def roadmaps_collection(request):
    user = get_authenticated_user(request)
    if user is None:
        return _auth_error()

    if request.method == "GET":
        return JsonResponse(list_roadmaps_for_user(user), safe=False)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    topic = str(payload.get("topic", "")).strip() or "General Learning Path"
    mode = normalize_mode(payload.get("mode", "learn"))
    force_roadmap = bool(payload.get("force_roadmap", False))

    if not force_roadmap and is_broad_topic(topic, mode=mode):
        plan = plan_curriculum(topic, mode=mode)
        return JsonResponse(
            {
                "kind": "curriculum_preview",
                "plan": plan,
            },
            status=200,
        )

    roadmap = create_roadmap_for_user(user, topic=topic, mode=mode)
    module_progress = _get_module_progress_map(user)
    return JsonResponse(
        {
            "kind": "roadmap",
            "roadmap": serialize_roadmap(roadmap, module_progress),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["GET"])
def roadmaps_detail(request, roadmap_id):
    user = get_authenticated_user(request)
    if user is None:
        return _auth_error()

    roadmap = get_roadmap_for_user(user, roadmap_id)
    module_progress = _get_module_progress_map(user)
    return JsonResponse(serialize_roadmap(roadmap, module_progress))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def curriculums_collection(request):
    user = get_authenticated_user(request)
    if user is None:
        return _auth_error()

    if request.method == "GET":
        return JsonResponse(list_curriculums_for_user(user), safe=False)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    topic = str(payload.get("topic", "")).strip() or "General Learning Path"
    mode = normalize_mode(payload.get("mode", "learn"))
    courses = payload.get("courses") or []
    if not isinstance(courses, list) or not courses:
        return JsonResponse(
            {"detail": "courses must be a non-empty list."},
            status=400,
        )

    try:
        curriculum = create_curriculum_for_user(
            user,
            topic=topic,
            mode=mode,
            courses=courses,
        )
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        serialize_curriculum_with_first_roadmap(curriculum, user),
        status=201,
    )


@csrf_exempt
@require_http_methods(["GET"])
def curriculums_detail(request, curriculum_id):
    user = get_authenticated_user(request)
    if user is None:
        return _auth_error()

    curriculum = get_curriculum_for_user(user, curriculum_id)
    module_progress = _get_module_progress_map(user)
    return JsonResponse(serialize_curriculum(curriculum, module_progress))


@csrf_exempt
@require_http_methods(["POST"])
def curriculum_course_expand(request, curriculum_id, course_id):
    user = get_authenticated_user(request)
    if user is None:
        return _auth_error()

    course = get_course_for_user(user, curriculum_id, course_id)
    roadmap = expand_course(course, user=user)
    module_progress = _get_module_progress_map(user)
    return JsonResponse(
        {
            "course_id": str(course.id),
            "curriculum_id": str(curriculum_id),
            "roadmap": serialize_roadmap(roadmap, module_progress),
        }
    )
