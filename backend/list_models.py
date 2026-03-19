import httpx, os, sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.') / '.env')
key = os.environ.get('OPENROUTER_API_KEY', '')
r = httpx.get('https://openrouter.ai/api/v1/models', headers={'Authorization': f'Bearer {key}'}, timeout=15)
models = [m for m in r.json().get('data', []) if ':free' in m['id']]

print('Free models with tool support:')
for m in models:
    supported = m.get('supported_parameters', [])
    if 'tools' in supported or 'tool_choice' in supported:
        print(f"  {m['id']} (ctx={m.get('context_length', 0)})")

print('\nAll free models:')
for m in sorted(models, key=lambda x: x['id']):
    print(f"  {m['id']}")
