import json
from hashlib import sha256

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.auth.services import (
    login_password_user,
    register_password_user,
    upsert_firebase_user,
)
from utils.firebase_auth import FirebaseAuthError, verify_firebase_token


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


@require_POST
def register(request):
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    email = str(payload.get("email", "")).strip()
    password = str(payload.get("password", ""))
    name = str(payload.get("name", "")).strip()

    if not email or not password or not name:
        return JsonResponse(
            {"detail": "email, password, and name are required."},
            status=400,
        )

    try:
        user, token = register_password_user(email, password, name)
    except ValueError:
        return JsonResponse({"detail": "User already exists."}, status=409)

    return JsonResponse({"session_token": token, "user": _user_payload(user)}, status=201)


@require_POST
def login(request):
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    email = str(payload.get("email", "")).strip()
    password = str(payload.get("password", ""))
    if not email or not password:
        return JsonResponse({"detail": "email and password are required."}, status=400)

    result = login_password_user(email, password)
    if result is None:
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    user, token = result
    return JsonResponse({"session_token": token, "user": _user_payload(user)})


@require_POST
def firebase_login(request):
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    id_token = str(payload.get("id_token", "")).strip()
    if not id_token:
        return JsonResponse({"detail": "id_token is required."}, status=400)

    try:
        decoded = verify_firebase_token(id_token)
        uid = decoded.get("uid") or f"fb-{sha256(id_token.encode()).hexdigest()[:10]}"
        email = decoded.get("email") or f"{uid}@firebase.local"
        name = decoded.get("name") or "Firebase User"
    except FirebaseAuthError:
        if not settings.AUTH_STUB_ALLOW_FIREBASE_FALLBACK:
            return JsonResponse({"detail": "Invalid or expired Firebase ID token."}, status=401)
        uid = f"fb-{sha256(id_token.encode()).hexdigest()[:10]}"
        email = f"{uid}@firebase.local"
        name = "Firebase User"

    user, token = upsert_firebase_user(uid=uid, email=email, name=name)
    return JsonResponse({"session_token": token, "user": _user_payload(user)})
