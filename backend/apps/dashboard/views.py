"""
Dashboard view — GET /api/dashboard.

Returns aggregated progress summaries, XP totals, streak info, and recent activity.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from utils.progress_store import get_dashboard


_DEFAULT_USER = "anonymous"


def _get_user_id(request) -> str:
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip() or _DEFAULT_USER
    return _DEFAULT_USER


@require_GET
def dashboard(request):
    """
    GET /api/dashboard

    Returns lesson counts, streak info, and progress summaries for the
    authenticated user. Falls back to "anonymous" when no auth header is present.
    """
    user_id = _get_user_id(request)
    data = get_dashboard(user_id)
    return JsonResponse(data)
