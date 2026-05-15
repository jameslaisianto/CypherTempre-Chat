"""ImageGen route handlers — generate, edit, redefine, and delete images."""

from __future__ import annotations

import base64
import uuid
from http import HTTPStatus
from typing import Any

from server.config import IMAGE_PROVIDERS
from server.llm import call_image_generation


def handle_imagegen_generate(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    prompt = str(payload.get("prompt", "")).strip()
    model = str(payload.get("model", IMAGE_PROVIDERS.get("openrouter", {}).get("default_model", ""))).strip()
    aspect_ratio = str(payload.get("aspect_ratio", "1:1")).strip() or "1:1"
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "openrouter")).strip() or "openrouter"
    if not prompt:
        handler.send_json({"ok": False, "error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not api_key:
        handler.send_json({"ok": False, "error": "API key is required"}, HTTPStatus.BAD_REQUEST)
        return
    messages = [{"role": "user", "content": prompt}]
    try:
        images = call_image_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=min(app.timeout, 120.0),
            modalities=["image"],
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return
    if not images:
        handler.send_json({"ok": False, "error": "No image was generated."})
        return
    image_id = uuid.uuid4().hex
    entry = app.add_gallery_image(
        user["username"],
        image_id=image_id,
        prompt=prompt,
        mode="generate",
        model=model,
        provider=provider,
        aspect_ratio=aspect_ratio,
        b64_data=images[0],
    )
    handler.send_json({
        "ok": True,
        "image": entry,
        "data_url": f"data:image/png;base64,{images[0]}",
    })


def handle_imagegen_edit(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    prompt = str(payload.get("prompt", "")).strip()
    image_data = str(payload.get("image", "")).strip()
    model = str(payload.get("model", "google/gemini-2.5-flash-image-preview")).strip()
    aspect_ratio = str(payload.get("aspect_ratio", "1:1")).strip() or "1:1"
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "openrouter")).strip() or "openrouter"
    if not prompt:
        handler.send_json({"ok": False, "error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not image_data:
        handler.send_json({"ok": False, "error": "image is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not api_key:
        handler.send_json({"ok": False, "error": "API key is required"}, HTTPStatus.BAD_REQUEST)
        return
    if image_data.startswith("data:image"):
        image_data = image_data.split(",", 1)[1]
    content: list[dict[str, Any]] = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
        {"type": "text", "text": prompt},
    ]
    messages = [{"role": "user", "content": content}]
    try:
        images = call_image_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=min(app.timeout, 120.0),
            modalities=["image", "text"],
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return
    if not images:
        handler.send_json({"ok": False, "error": "No image was generated."})
        return
    image_id = uuid.uuid4().hex
    entry = app.add_gallery_image(
        user["username"],
        image_id=image_id,
        prompt=prompt,
        mode="edit",
        model=model,
        provider=provider,
        aspect_ratio=aspect_ratio,
        b64_data=images[0],
    )
    handler.send_json({
        "ok": True,
        "image": entry,
        "data_url": f"data:image/png;base64,{images[0]}",
    })


def handle_imagegen_redefine(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    source_id = str(payload.get("source_id", "")).strip()
    prompt = str(payload.get("prompt", "")).strip()
    model = str(payload.get("model", IMAGE_PROVIDERS.get("openrouter", {}).get("default_model", ""))).strip()
    aspect_ratio = str(payload.get("aspect_ratio", "1:1")).strip() or "1:1"
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "openrouter")).strip() or "openrouter"
    if not source_id:
        handler.send_json({"ok": False, "error": "source_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not prompt:
        handler.send_json({"ok": False, "error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not api_key:
        handler.send_json({"ok": False, "error": "API key is required"}, HTTPStatus.BAD_REQUEST)
        return
    img_path = app.gallery_image_path(user["username"], source_id)
    if not img_path.exists():
        handler.send_json({"ok": False, "error": "Source image not found"}, HTTPStatus.NOT_FOUND)
        return
    b64_data = base64.b64encode(img_path.read_bytes()).decode("ascii")
    content: list[dict[str, Any]] = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_data}"}},
        {"type": "text", "text": prompt},
    ]
    messages = [{"role": "user", "content": content}]
    try:
        images = call_image_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=min(app.timeout, 120.0),
            modalities=["image", "text"],
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return
    if not images:
        handler.send_json({"ok": False, "error": "No image was generated."})
        return
    image_id = uuid.uuid4().hex
    entry = app.add_gallery_image(
        user["username"],
        image_id=image_id,
        prompt=prompt,
        mode="redefine",
        model=model,
        provider=provider,
        aspect_ratio=aspect_ratio,
        source_id=source_id,
        b64_data=images[0],
    )
    handler.send_json({
        "ok": True,
        "image": entry,
        "data_url": f"data:image/png;base64,{images[0]}",
    })


def handle_imagegen_delete(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    image_id = str(payload.get("image_id", "")).strip()
    if not image_id:
        handler.send_json({"ok": False, "error": "image_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    ok = app.delete_gallery_image(user["username"], image_id)
    handler.send_json({"ok": ok})
