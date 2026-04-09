from __future__ import annotations

from hashlib import sha256
from secrets import token_urlsafe
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.auth.models import SessionToken
from apps.users.models import User


SESSION_TTL = timedelta(days=30)


def _generate_session_token() -> str:
    return f"session-{token_urlsafe(32)}"


def _hash_session_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def get_user_for_session_token(token: str):
    normalized_token = str(token).strip()
    if not normalized_token:
        return None

    token_hash = _hash_session_token(normalized_token)
    session = (
        SessionToken.objects.select_related("user")
        .filter(
            token_hash=token_hash,
            revoked_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        .first()
    )
    if session is not None:
        return session.user

    return None


def resolve_user_from_bearer_token(token: str, *, allow_firebase_fallback: bool = False):
    user = get_user_for_session_token(token)
    if user is not None:
        return user

    if not allow_firebase_fallback:
        return None

    normalized_token = str(token).strip()
    if not normalized_token:
        return None

    fallback_user = User.objects.filter(firebase_uid=normalized_token).first()
    if fallback_user is not None:
        return fallback_user

    return User.objects.upsert_firebase_user(
        uid=normalized_token,
        email=f"{normalized_token}@firebase.local",
        name="Firebase User",
    )


@transaction.atomic
def create_session_for_user(user: User) -> str:
    token = _generate_session_token()
    SessionToken.objects.create(
        user=user,
        token_hash=_hash_session_token(token),
        expires_at=timezone.now() + SESSION_TTL,
    )
    return token


@transaction.atomic
def register_password_user(email: str, password: str, name: str):
    user = User.objects.create_password_user(email=email, password=password, name=name)
    return user, create_session_for_user(user)


@transaction.atomic
def login_password_user(email: str, password: str):
    user = User.objects.authenticate_password(email=email, password=password)
    if user is None:
        return None
    return user, create_session_for_user(user)


@transaction.atomic
def upsert_firebase_user(uid: str, email: str, name: str):
    user = User.objects.upsert_firebase_user(uid=uid, email=email, name=name)
    return user, create_session_for_user(user)


@transaction.atomic
def reset_auth_store() -> None:
    SessionToken.objects.all().delete()
    User.objects.all().delete()
