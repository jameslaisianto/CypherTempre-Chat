"""AudioGen route handlers — text-to-speech generation via Morpheus."""

from __future__ import annotations

import base64
import uuid
from http import HTTPStatus
from typing import Any

from server.config import AUDIO_PROVIDERS
from server.llm import call_audio_generation


def handle_audiogen_generate(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return

    payload = handler.read_json()
    text = str(payload.get("text", "")).strip()
    model = str(payload.get("model", AUDIO_PROVIDERS.get("morpheus", {}).get("default_model", "tts-1"))).strip()
    voice = str(payload.get("voice", "af_alloy")).strip() or "af_alloy"
    response_format = str(payload.get("response_format", "mp3")).strip() or "mp3"
    speed = float(payload.get("speed", 1.0))
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "morpheus")).strip() or "morpheus"

    if not text:
        handler.send_json({"ok": False, "error": "text is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not api_key:
        handler.send_json({"ok": False, "error": "API key is required"}, HTTPStatus.BAD_REQUEST)
        return

    try:
        audio_data = call_audio_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            text=text,
            voice=voice,
            response_format=response_format,
            speed=speed,
            timeout=min(app.timeout, 60.0),
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return

    if not audio_data:
        handler.send_json({"ok": False, "error": "No audio was generated."})
        return

    # Return audio data as base64-encoded string for client playback
    audio_id = uuid.uuid4().hex
    handler.send_json({
        "ok": True,
        "audio_id": audio_id,
        "audio_data": audio_data,  # base64-encoded
        "format": response_format,
    })
