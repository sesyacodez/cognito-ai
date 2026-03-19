from uuid import uuid4


def get_placeholder_roadmap(topic: str) -> dict:
    """
    Returns a static 5-module roadmap in the normalized API contract shape.
    Used as a graceful fallback when the agent runner is unavailable.
    """
    topic_clean = topic.strip() or "General Learning Path"

    return {
        "roadmap_id": f"placeholder-{uuid4().hex[:8]}",
        "mode": "learn",
        "modules": [
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 0,
                "title": f"{topic_clean}: Foundations",
                "outcome": "Learn the basics and fundamental concepts.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 1,
                "title": f"{topic_clean}: Core Concepts",
                "outcome": "Explore the essential principles and theories.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 2,
                "title": f"{topic_clean}: Intermediate Techniques",
                "outcome": "Develop intermediate skills and apply techniques.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 3,
                "title": f"{topic_clean}: Advanced Applications",
                "outcome": "Master advanced applications and real-world use cases.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 4,
                "title": f"{topic_clean}: Capstone Project",
                "outcome": "Complete a capstone project to demonstrate your learning.",
            },
        ],
    }
