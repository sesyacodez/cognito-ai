import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                (
                    "firebase_uid",
                    models.CharField(blank=True, max_length=255, null=True, unique=True),
                ),
                (
                    "auth_provider",
                    models.CharField(
                        choices=[("firebase", "Firebase"), ("password", "Password")],
                        default="password",
                        max_length=20,
                    ),
                ),
                (
                    "password_hash",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "users",
            },
        ),
    ]
