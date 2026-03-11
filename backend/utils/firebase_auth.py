from typing import Any

from firebase_admin import auth, get_app, initialize_app


class FirebaseAuthError(Exception):
    """Raised when Firebase token verification fails."""


def _ensure_firebase_app() -> None:
    try:
        get_app()
    except ValueError:
        initialize_app()


def verify_firebase_token(id_token: str) -> dict[str, str]:
    if not id_token or not id_token.strip():
        raise FirebaseAuthError("Missing Firebase ID token.")

    try:
        _ensure_firebase_app()
        decoded: dict[str, Any] = auth.verify_id_token(id_token)
    except Exception as exc:
        raise FirebaseAuthError("Invalid or expired Firebase ID token.") from exc

    uid = str(decoded.get("uid", "")).strip()
    if not uid:
        raise FirebaseAuthError("Firebase token is missing uid.")

    return {
        "uid": uid,
        "email": str(decoded.get("email", "")).strip(),
        "name": str(decoded.get("name", "")).strip(),
    }
