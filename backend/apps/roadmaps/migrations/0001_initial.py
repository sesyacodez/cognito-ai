import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Roadmap",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("topic", models.CharField(max_length=255)),
                (
                    "mode",
                    models.CharField(
                        choices=[("learn", "Learn"), ("solve", "Solve")],
                        default="learn",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roadmaps",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "roadmaps",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="RoadmapModule",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("index", models.IntegerField()),
                ("outcome", models.TextField()),
                (
                    "roadmap",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="modules",
                        to="roadmaps.roadmap",
                    ),
                ),
            ],
            options={
                "db_table": "modules",
                "ordering": ["index"],
            },
        ),
        migrations.AddConstraint(
            model_name="roadmapmodule",
            constraint=models.UniqueConstraint(fields=["roadmap", "index"], name="unique_module_index_per_roadmap"),
        ),
        migrations.AddConstraint(
            model_name="roadmapmodule",
            constraint=models.CheckConstraint(condition=models.Q(index__gte=0), name="module_index_non_negative"),
        ),
    ]