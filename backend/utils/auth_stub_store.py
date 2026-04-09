"""Compatibility wrappers for the database-backed auth service."""

from apps.auth.services import (  # noqa: F401
    login_password_user,
    register_password_user,
    reset_auth_store,
    upsert_firebase_user,
)

