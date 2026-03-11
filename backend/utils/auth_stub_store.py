from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass
class StubUser:
    id: str
    email: str
    name: str
    password: str | None = None
    firebase_uid: str | None = None


USERS_BY_EMAIL: dict[str, StubUser] = {}


def reset_auth_store() -> None:
    USERS_BY_EMAIL.clear()


def _session_token() -> str:
    return f"stub-session-{uuid4().hex}"


def register_password_user(email: str, password: str, name: str) -> tuple[StubUser, str]:
    normalized = email.strip().lower()
    if normalized in USERS_BY_EMAIL:
        raise ValueError("User already exists")

    user = StubUser(
        id=f"user-{uuid4().hex[:10]}",
        email=normalized,
        name=name.strip(),
        password=password,
    )
    USERS_BY_EMAIL[normalized] = user
    return user, _session_token()


def login_password_user(email: str, password: str) -> tuple[StubUser, str] | None:
    normalized = email.strip().lower()
    user = USERS_BY_EMAIL.get(normalized)
    if not user or user.password != password:
        return None
    return user, _session_token()


def upsert_firebase_user(uid: str, email: str, name: str) -> tuple[StubUser, str]:
    normalized = email.strip().lower()
    user = USERS_BY_EMAIL.get(normalized)
    if user is None:
        user = StubUser(
            id=f"user-{uuid4().hex[:10]}",
            email=normalized,
            name=name.strip() or "Firebase User",
            firebase_uid=uid,
        )
        USERS_BY_EMAIL[normalized] = user
    else:
        user.firebase_uid = uid
        if name.strip():
            user.name = name.strip()

    return user, _session_token()
