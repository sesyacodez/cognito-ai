import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Setup Django environment
load_dotenv(Path('.') / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from agent.runner import run_skill, AgentError

def test_lesson_generation():
    print("\n--- Testing Lesson Generator ---")
    try:
        # Test lesson generation for a specific topic
        lesson = run_skill('lesson_generator', mode='learn', module_topic='Python Lists')
        print("SUCCESS! Full Lesson generated:")
        print(json.dumps(lesson, indent=2))
        return lesson
    except AgentError as e:
        print(f"Error generating lesson: {e}")
        return None

def test_socratic_tutor(lesson):
    if not lesson or not lesson.get('questions'):
        return
    
    print("\n--- Testing Socratic Tutor (Evaluation) ---")
    q = lesson['questions'][0]
    print(f"Question: {q['prompt']}")
    print(f"Expected: {q['answer_key']}")
    
    student_answer = "You use them to store multiple items in one variable."
    print(f"Student Answer: {student_answer}")
    
    try:
        evaluation = run_skill(
            'socratic_tutor', 
            mode='learn', 
            student_answer=student_answer,
            question_prompt=f"{q['prompt']}\nExpected Answer: {q['answer_key']}"
        )
        print("Evaluation Response:")
        print(json.dumps(evaluation, indent=2))
    except AgentError as e:
        print(f"Error in evaluation: {e}")

if __name__ == "__main__":
    generated_lesson = test_lesson_generation()
    test_socratic_tutor(generated_lesson)
