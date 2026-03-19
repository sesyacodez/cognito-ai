from uuid import uuid4
from pydantic import BaseModel, Field, ValidationError, model_validator


class DecomposerModule(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    order: int = Field(ge=1)


class RoadmapPayload(BaseModel):
    topic: str = Field(min_length=1)
    modules: list[DecomposerModule]

    @model_validator(mode="after")
    def validate_modules(self):
        count = len(self.modules)
        if count < 1 or count > 7:
            raise ValueError(
                f"roadmap.modules must contain between 1 and 7 modules, got {count}"
            )

        orders = [module.order for module in self.modules]
        if len(set(orders)) != count:
            raise ValueError("roadmap.modules order values must be unique")

        expected = list(range(1, count + 1))
        if sorted(orders) != expected:
            raise ValueError(
                f"roadmap.modules order values must be sequential from 1, got {sorted(orders)}"
            )

        return self


class DecomposerOutput(BaseModel):
    roadmap: RoadmapPayload


def normalize_decomposer_output(data: dict, mode: str = "learn") -> dict:
    validated = DecomposerOutput.model_validate(data)
    sorted_modules = sorted(validated.roadmap.modules, key=lambda m: m.order)

    return {
        "roadmap_id": str(uuid4()),
        "mode": mode,
        "modules": [
            {
                "id": module.id,
                "title": module.title,
                "outcome": module.outcome,
                "index": module.order - 1,
            }
            for module in sorted_modules
        ],
    }


__all__ = [
    "DecomposerModule",
    "RoadmapPayload",
    "DecomposerOutput",
    "normalize_decomposer_output",
    "ValidationError",
]
