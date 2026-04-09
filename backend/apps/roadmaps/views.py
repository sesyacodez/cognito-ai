import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from agent.runner import AgentError, run_skill
from utils.fixtures import get_placeholder_roadmap


@csrf_exempt
@require_http_methods(["GET", "POST"])
def roadmaps_collection(request):
    if request.method == "GET":
        return JsonResponse([], safe=False)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    topic = str(payload.get("topic", "")).strip() or "General Learning Path"
    mode = str(payload.get("mode", "learn")).strip()
    if mode not in ("learn", "solve"):
        mode = "learn"

    try:
        response = run_skill("decomposer", mode=mode, topic=topic)
    except AgentError:
        response = get_placeholder_roadmap(topic)

    return JsonResponse(response, status=201)
