import base64
import json
import os

import httpx
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


@csrf_exempt
@require_http_methods(["POST"])
def image_to_text(request):
    """Accept a base64-encoded image and return the text/content extracted by a vision LLM."""
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    image_b64 = payload.get("image")
    mime_type = payload.get("mime_type", "image/png")

    if not image_b64:
        return JsonResponse({"detail": "Missing 'image' field (base64)."}, status=400)

    if len(image_b64) > MAX_IMAGE_SIZE * 4 / 3:
        return JsonResponse({"detail": "Image too large (max 10 MB)."}, status=400)

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return JsonResponse({"detail": "Vision service unavailable."}, status=503)

    model = os.environ.get("VISION_MODEL", os.environ.get("DECOMPOSER_MODEL", "google/gemini-2.5-flash"))

    data_uri = f"data:{mime_type};base64,{image_b64}"

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert at reading images. Extract ALL text, numbers, "
                "mathematical expressions, and symbols from the image exactly as they appear. "
                "Preserve the original formatting and symbols (e.g. ÷ × + − = ≥ ≤). "
                "If the image contains a math problem, reproduce the full expression. "
                "Return ONLY the extracted text, nothing else — no explanations or commentary."
            ),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": data_uri},
                },
                {
                    "type": "text",
                    "text": "Extract all text and symbols from this image exactly as they appear.",
                },
            ],
        },
    ]

    try:
        resp = httpx.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://cognito.ai",
                "X-Title": "Cognito AI",
            },
            json={"model": model, "messages": messages},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        return JsonResponse({"text": text})
    except httpx.HTTPStatusError as exc:
        return JsonResponse(
            {"detail": f"Vision model error ({exc.response.status_code})."},
            status=502,
        )
    except (httpx.RequestError, KeyError, IndexError):
        return JsonResponse({"detail": "Failed to process image."}, status=502)
