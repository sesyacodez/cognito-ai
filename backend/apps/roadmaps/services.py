from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.auth.services import resolve_user_from_bearer_token
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


def serialize_roadmap(roadmap: Roadmap) -> dict:
    return roadmap.to_api_dict()


def list_roadmaps_for_user(user) -> list[dict]:
    roadmaps = (
        Roadmap.objects.filter(user=user)
        .prefetch_related("modules")
        .order_by("-created_at")
    )
    return [serialize_roadmap(roadmap) for roadmap in roadmaps]


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