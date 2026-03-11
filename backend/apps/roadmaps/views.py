import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from utils.fixtures import get_placeholder_roadmap


@require_http_methods(["GET", "POST"])
def roadmaps_collection(request):
    if request.method == "GET":
        return JsonResponse([], safe=False)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    topic = str(payload.get("topic", "")).strip() or "General Learning Path"
    response = get_placeholder_roadmap(topic)
    return JsonResponse(response, status=201)
