from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.auth.services import resolve_user_from_bearer_token
from apps.lessons.models import LessonState
from apps.roadmaps.models import Roadmap, RoadmapModule
from utils.fixtures import get_placeholder_roadmap


def normalize_mode(mode: str) -> str:
    return "solve" if str(mode).strip().lower() == "solve" else "learn"


def extract_bearer_token(request) -> str | None:
    header = request.headers.get("Authorization", "").strip()
    if not header.lower().startswith("bearer "):
        return None

    token = header.split(" ", 1)[1].strip()
    return token or None


def get_authenticated_user(request):
    token = extract_bearer_token(request)
    if token is None:
        return None

    return resolve_user_from_bearer_token(
        token,
        allow_firebase_fallback=settings.AUTH_STUB_ALLOW_FIREBASE_FALLBACK,
    )


def serialize_roadmap(roadmap: Roadmap, module_progress: dict | None = None) -> dict:
    data = roadmap.to_api_dict()
    if module_progress:
        for module in data.get("modules", []):
            lesson_key = f"{roadmap.id}-{module['index']}"
            state = module_progress.get(lesson_key)
            if state:
                module["lesson_status"] = state["status"]
                module["xp_earned"] = state["xp_earned"]
                module["stars_remaining"] = state["stars_remaining"]
            else:
                module["lesson_status"] = "not_started"
                module["xp_earned"] = 0
                module["stars_remaining"] = 3

        completed_count = sum(
            1 for m in data.get("modules", [])
            if m.get("lesson_status") == "completed"
        )
        total = len(data.get("modules", []))
        data["progress"] = int(round((completed_count / total) * 100)) if total else 0
    return data


def _get_module_progress_map(user) -> dict:
    states = (
        LessonState.objects
        .filter(user=user)
        .select_related("lesson")
    )
    return {
        state.lesson.lesson_key: {
            "status": state.status,
            "xp_earned": state.xp_earned,
            "stars_remaining": state.stars_remaining,
        }
        for state in states
    }


def list_roadmaps_for_user(user) -> list[dict]:
    roadmaps = (
        Roadmap.objects.filter(user=user)
        .prefetch_related("modules")
        .order_by("-created_at")
    )
    module_progress = _get_module_progress_map(user)
    return [serialize_roadmap(roadmap, module_progress) for roadmap in roadmaps]


def get_roadmap_for_user(user, roadmap_id):
    return get_object_or_404(
        Roadmap.objects.prefetch_related("modules"),
        id=roadmap_id,
        user=user,
    )


@transaction.atomic
def create_roadmap_for_user(user, topic: str, mode: str) -> Roadmap:
    normalized_topic = str(topic).strip() or "General Learning Path"
    normalized_mode = normalize_mode(mode)

    roadmap = Roadmap.objects.create(
        user=user,
        topic=normalized_topic,
        mode=normalized_mode,
    )

    placeholder = get_placeholder_roadmap(normalized_topic)
    modules = []
    for fallback_index, module_data in enumerate(placeholder.get("modules", [])):
        modules.append(
            RoadmapModule(
                roadmap=roadmap,
                title=str(module_data.get("title", "")).strip() or normalized_topic,
                index=int(module_data.get("index", fallback_index)),
                outcome=str(module_data.get("outcome", "")).strip() or "Learn the basics and fundamental concepts.",
            )
        )

    RoadmapModule.objects.bulk_create(modules)
    return roadmap