import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.') / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from agent.runner import run_skill, AgentError

print("Testing decomposer skill with qwen3-coder...")
try:
    result = run_skill('decomposer', mode='learn', topic='Python basics')
    print("SUCCESS!")
    print(f"  roadmap_id: {result['roadmap_id']}")
    print(f"  mode: {result['mode']}")
    print(f"  modules ({len(result['modules'])}):")
    for m in result['modules']:
        print(f"    [{m['index']}] {m['title']}")
except AgentError as e:
    print("AgentError:", e)
except Exception as e:
    print(f"Unexpected {type(e).__name__}: {e}")
