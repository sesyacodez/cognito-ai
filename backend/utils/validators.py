from pydantic import BaseModel, Field, ValidationError, model_validator


class DecomposerModule(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    order: int = Field(ge=1, le=5)


class RoadmapPayload(BaseModel):
    topic: str = Field(min_length=1)
    modules: list[DecomposerModule]

    @model_validator(mode="after")
    def validate_modules(self):
        if len(self.modules) != 5:
            raise ValueError("roadmap.modules must contain exactly 5 modules")

        orders = [module.order for module in self.modules]
        if len(set(orders)) != 5:
            raise ValueError("roadmap.modules order values must be unique")
        if sorted(orders) != [1, 2, 3, 4, 5]:
            raise ValueError("roadmap.modules order values must be 1 through 5")

        return self


class DecomposerOutput(BaseModel):
    roadmap: RoadmapPayload


def normalize_decomposer_output(data: dict) -> dict:
    validated = DecomposerOutput.model_validate(data)
    sorted_modules = sorted(validated.roadmap.modules, key=lambda module: module.order)

    return {
        "roadmap_id": "placeholder-normalized",
        "modules": [
            {
                "id": module.id,
                "title": module.title,
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
