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


class LessonQuestion(BaseModel):
    id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    difficulty: str = Field(pattern="^(easy|medium|hard)$")
    answer_key: str = Field(min_length=1)


class LessonPayload(BaseModel):
    micro_theory: str = Field(min_length=1, max_length=1000)  # ~120-150 words limit
    questions: list[LessonQuestion]

    @model_validator(mode="after")
    def validate_questions(self):
        if len(self.questions) != 3:
            raise ValueError("lesson.questions must contain exactly 3 questions")
        return self


class LessonOutput(BaseModel):
    lesson: LessonPayload


class SocraticEvaluation(BaseModel):
    correct: bool
    next_prompt: str
    hint: str | None = None


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


def normalize_lesson_output(data: dict, mode: str = "learn") -> dict:
    validated = LessonOutput.model_validate(data)
    return {
        "lesson_id": str(uuid4()),
        "mode": mode,
        "micro_theory": validated.lesson.micro_theory,
        "questions": [
            {
                "id": q.id,
                "prompt": q.prompt,
                "difficulty": q.difficulty,
                "answer_key": q.answer_key,
            }
            for q in validated.lesson.questions
        ],
    }


def normalize_evaluation_output(data: dict) -> dict:
    validated = SocraticEvaluation.model_validate(data)
    return validated.model_dump()


__all__ = [
    "DecomposerModule",
    "RoadmapPayload",
    "DecomposerOutput",
    "normalize_decomposer_output",
    "LessonQuestion",
    "LessonPayload",
    "LessonOutput",
    "SocraticEvaluation",
    "normalize_lesson_output",
    "normalize_evaluation_output",
    "ValidationError",
]
