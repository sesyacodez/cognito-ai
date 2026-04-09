import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.roadmaps.services import (
    create_roadmap_for_user,
    get_authenticated_user,
    get_roadmap_for_user,
    list_roadmaps_for_user,
    normalize_mode,
    serialize_roadmap,
)


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
    roadmap = create_roadmap_for_user(user, topic=topic, mode=mode)
    return JsonResponse(serialize_roadmap(roadmap), status=201)


@csrf_exempt
@require_http_methods(["GET"])
def roadmaps_detail(request, roadmap_id):
    user = get_authenticated_user(request)
    if user is None:
        return _auth_error()

    roadmap = get_roadmap_for_user(user, roadmap_id)
    return JsonResponse(serialize_roadmap(roadmap))