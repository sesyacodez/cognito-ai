from __future__ import annotations

import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models, transaction


class UserManager(models.Manager):
	def _normalize_email(self, email: str) -> str:
		return str(email).strip().lower()

	def _normalize_name(self, name: str) -> str:
		return str(name).strip()

	@transaction.atomic
	def create_password_user(self, email: str, password: str, name: str):
		normalized_email = self._normalize_email(email)
		if not normalized_email:
			raise ValueError("email is required")

		if not password or not str(password).strip():
			raise ValueError("password is required")

		if self.filter(email=normalized_email).exists():
			raise ValueError("User already exists")

		user = self.model(
			email=normalized_email,
			name=self._normalize_name(name),
			auth_provider=User.AuthProvider.PASSWORD,
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	@transaction.atomic
	def authenticate_password(self, email: str, password: str):
		normalized_email = self._normalize_email(email)
		user = self.filter(email=normalized_email).first()
		if user is None or not user.check_password(password):
			return None
		return user

	@transaction.atomic
	def upsert_firebase_user(self, uid: str, email: str, name: str):
		firebase_uid = str(uid).strip()
		normalized_email = self._normalize_email(email)
		normalized_name = self._normalize_name(name)

		if not firebase_uid:
			raise ValueError("Firebase uid is required")
		if not normalized_email:
			raise ValueError("email is required")

		user = self.select_for_update().filter(firebase_uid=firebase_uid).first()
		if user is None:
			user = self.select_for_update().filter(email=normalized_email).first()

		if user is None:
			user = self.model(
				firebase_uid=firebase_uid,
				auth_provider=User.AuthProvider.FIREBASE,
				email=normalized_email,
				name=normalized_name or "Firebase User",
			)
		else:
			user.firebase_uid = firebase_uid
			user.auth_provider = User.AuthProvider.FIREBASE
			user.email = normalized_email
			if normalized_name:
				user.name = normalized_name

		user.save(using=self._db)
		return user


class User(models.Model):
	class AuthProvider(models.TextChoices):
		FIREBASE = "firebase", "Firebase"
		PASSWORD = "password", "Password"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
	auth_provider = models.CharField(
		max_length=20,
		choices=AuthProvider.choices,
		default=AuthProvider.PASSWORD,
	)
	password_hash = models.CharField(max_length=128, null=True, blank=True)
	email = models.EmailField(unique=True)
	name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)

	objects = UserManager()

	class Meta:
		db_table = "users"

	def set_password(self, raw_password: str) -> None:
		self.password_hash = make_password(raw_password)

	def check_password(self, raw_password: str) -> bool:
		if not self.password_hash:
			return False
		return check_password(raw_password, self.password_hash)

	def __str__(self) -> str:
		return self.email
