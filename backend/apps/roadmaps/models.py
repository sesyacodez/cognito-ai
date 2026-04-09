from __future__ import annotations

import uuid

from django.db import models

from apps.users.models import User


class Roadmap(models.Model):
	class Mode(models.TextChoices):
		LEARN = "learn", "Learn"
		SOLVE = "solve", "Solve"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roadmaps")
	topic = models.CharField(max_length=255)
	mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.LEARN)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "roadmaps"
		ordering = ["-created_at"]

	def journey_type(self) -> str:
		return "problem" if self.mode == self.Mode.SOLVE else "topic"

	def to_api_dict(self) -> dict:
		created_at = self.created_at.isoformat()
		modules = [module.to_api_dict() for module in self.modules.all()]
		return {
			"roadmap_id": str(self.id),
			"id": str(self.id),
			"topic": self.topic,
			"mode": self.mode,
			"type": self.journey_type(),
			"created_at": created_at,
			"createdAt": created_at,
			"progress": 0,
			"modules": modules,
		}


class RoadmapModule(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="modules")
	title = models.CharField(max_length=255)
	index = models.IntegerField()
	outcome = models.TextField()

	class Meta:
		db_table = "modules"
		ordering = ["index"]
		constraints = [
			models.UniqueConstraint(fields=["roadmap", "index"], name="unique_module_index_per_roadmap"),
			models.CheckConstraint(condition=models.Q(index__gte=0), name="module_index_non_negative"),
		]

	def to_api_dict(self) -> dict:
		return {
			"id": str(self.id),
			"title": self.title,
			"index": self.index,
			"order": self.index + 1,
			"outcome": self.outcome,
			"description": self.outcome,
		}
