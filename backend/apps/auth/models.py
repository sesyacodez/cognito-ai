from __future__ import annotations

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.users.models import User


class SessionToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="session_tokens")
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_sessions"

    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > timezone.now()
