from uuid import uuid4


def get_placeholder_roadmap(topic: str) -> dict:
    topic_clean = topic.strip() or "General Learning Path"

    return {
        "roadmap_id": f"placeholder-{uuid4().hex[:8]}",
        "modules": [
            {"id": "m1", "title": f"{topic_clean}: Foundations", "index": 0},
            {"id": "m2", "title": f"{topic_clean}: Core Concepts", "index": 1},
            {"id": "m3", "title": f"{topic_clean}: Intermediate Techniques", "index": 2},
            {"id": "m4", "title": f"{topic_clean}: Advanced Applications", "index": 3},
            {"id": "m5", "title": f"{topic_clean}: Capstone Project", "index": 4},
        ],
    }
