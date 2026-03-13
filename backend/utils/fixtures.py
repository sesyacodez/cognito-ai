from uuid import uuid4


def get_placeholder_roadmap(topic: str) -> dict:
    topic_clean = topic.strip() or "General Learning Path"

    return {
        "id": f"placeholder-{uuid4().hex[:8]}",
        "topic": topic_clean,
        "modules": [
            {
                "order": 0,
                "title": f"{topic_clean}: Foundations",
                "description": "Learn the basics and fundamental concepts."
            },
            {
                "order": 1,
                "title": f"{topic_clean}: Core Concepts",
                "description": "Explore the essential principles and theories."
            },
            {
                "order": 2,
                "title": f"{topic_clean}: Intermediate Techniques",
                "description": "Develop intermediate skills and apply techniques."
            },
            {
                "order": 3,
                "title": f"{topic_clean}: Advanced Applications",
                "description": "Master advanced applications and real-world use cases."
            },
            {
                "order": 4,
                "title": f"{topic_clean}: Capstone Project",
                "description": "Complete a capstone project to demonstrate your learning."
            },
        ],
    }
