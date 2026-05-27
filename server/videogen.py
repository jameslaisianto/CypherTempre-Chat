"""VideoGen (CineTempre) route handlers — generate, image-to-video, remix/extend, delete.

Mirrors server/imagegen.py structure but for short cinematic clips with
temporal lineage in a dedicated per-user videogen Timechain.
"""

from __future__ import annotations

import base64
import uuid
from http import HTTPStatus
from typing import Any

from server.config import VIDEO_PROVIDERS
from server.llm import call_video_generation


def handle_videogen_generate(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    prompt = str(payload.get("prompt", "")).strip()
    model = str(payload.get("model", VIDEO_PROVIDERS.get("openrouter", {}).get("default_model", ""))).strip()
    aspect_ratio = str(payload.get("aspect_ratio", "16:9")).strip() or "16:9"
    duration = str(payload.get("duration", "8s")).strip() or "8s"
    motion_preset = str(payload.get("motion_preset", "Static")).strip() or "Static"
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "openrouter")).strip() or "openrouter"
    if not prompt:
        handler.send_json({"ok": False, "error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
        return
    if provider != "demo" and not api_key:
        handler.send_json({"ok": False, "error": "API key is required"}, HTTPStatus.BAD_REQUEST)
        return

    messages = [{"role": "user", "content": prompt}]
    try:
        result = call_video_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=min(app.timeout, 180.0),
            aspect_ratio=aspect_ratio,
            duration=duration,
            motion_preset=motion_preset,
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return

    video_id = uuid.uuid4().hex
    entry = app.add_gallery_video(
        user["username"],
        video_id=video_id,
        prompt=prompt,
        mode="generate",
        model=model,
        provider=provider,
        aspect_ratio=aspect_ratio,
        duration=duration,
        motion_preset=motion_preset,
        b64_data=result.get("b64", ""),
        video_url=result.get("url", ""),
    )
    handler.send_json({
        "ok": True,
        "video": entry,
        "data_url": result.get("data_url", ""),
        "video_url": result.get("url", ""),
    })


def handle_videogen_img2vid(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    prompt = str(payload.get("prompt", "")).strip()
    image_data = str(payload.get("image", "")).strip()
    model = str(payload.get("model", VIDEO_PROVIDERS.get("openrouter", {}).get("default_model", ""))).strip()
    aspect_ratio = str(payload.get("aspect_ratio", "16:9")).strip() or "16:9"
    duration = str(payload.get("duration", "8s")).strip() or "8s"
    motion_preset = str(payload.get("motion_preset", "Dolly In")).strip() or "Dolly In"
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "openrouter")).strip() or "openrouter"
    if not prompt:
        handler.send_json({"ok": False, "error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not image_data:
        handler.send_json({"ok": False, "error": "image is required"}, HTTPStatus.BAD_REQUEST)
        return
    if provider != "demo" and not api_key:
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
        result = call_video_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=min(app.timeout, 180.0),
            aspect_ratio=aspect_ratio,
            duration=duration,
            motion_preset=motion_preset,
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return

    video_id = uuid.uuid4().hex
    entry = app.add_gallery_video(
        user["username"],
        video_id=video_id,
        prompt=prompt,
        mode="img2vid",
        model=model,
        provider=provider,
        aspect_ratio=aspect_ratio,
        duration=duration,
        motion_preset=motion_preset,
        b64_data=result.get("b64", ""),
        video_url=result.get("url", ""),
    )
    handler.send_json({
        "ok": True,
        "video": entry,
        "data_url": result.get("data_url", ""),
        "video_url": result.get("url", ""),
    })


def handle_videogen_remix(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    source_id = str(payload.get("source_id", "")).strip()
    prompt = str(payload.get("prompt", "")).strip()
    model = str(payload.get("model", VIDEO_PROVIDERS.get("openrouter", {}).get("default_model", ""))).strip()
    aspect_ratio = str(payload.get("aspect_ratio", "16:9")).strip() or "16:9"
    duration = str(payload.get("duration", "8s")).strip() or "8s"
    motion_preset = str(payload.get("motion_preset", "Remix")).strip() or "Remix"
    api_key = str(payload.get("apiKey", app.api_key)).strip() or app.api_key
    provider = str(payload.get("provider", "openrouter")).strip() or "openrouter"
    if not source_id:
        handler.send_json({"ok": False, "error": "source_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    if not prompt:
        handler.send_json({"ok": False, "error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
        return
    if provider != "demo" and not api_key:
        handler.send_json({"ok": False, "error": "API key is required"}, HTTPStatus.BAD_REQUEST)
        return

    vid_path = app.videogen_video_path(user["username"], source_id)
    if not vid_path.exists():
        handler.send_json({"ok": False, "error": "Source video not found"}, HTTPStatus.NOT_FOUND)
        return

    # For remix we send the source video as a reference (provider-dependent).
    # Many video remix endpoints accept a video_url or bytes. We pass a data URL if small.
    b64 = ""
    try:
        b64 = base64.b64encode(vid_path.read_bytes()).decode("ascii")
    except Exception:
        pass

    content: list[dict[str, Any]] = [
        {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{b64}"}} if b64 else {"type": "text", "text": "source video"},
        {"type": "text", "text": prompt},
    ]
    messages = [{"role": "user", "content": content}]
    try:
        result = call_video_generation(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=min(app.timeout, 180.0),
            aspect_ratio=aspect_ratio,
            duration=duration,
            motion_preset=motion_preset,
        )
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)})
        return

    video_id = uuid.uuid4().hex
    entry = app.add_gallery_video(
        user["username"],
        video_id=video_id,
        prompt=prompt,
        mode="remix",
        model=model,
        provider=provider,
        aspect_ratio=aspect_ratio,
        duration=duration,
        motion_preset=motion_preset,
        source_id=source_id,
        b64_data=result.get("b64", ""),
        video_url=result.get("url", ""),
    )
    handler.send_json({
        "ok": True,
        "video": entry,
        "data_url": result.get("data_url", ""),
        "video_url": result.get("url", ""),
    })


def handle_videogen_delete(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    video_id = str(payload.get("video_id", "")).strip()
    if not video_id:
        handler.send_json({"ok": False, "error": "video_id is required"}, HTTPStatus.BAD_REQUEST)
        return
    ok = app.delete_gallery_video(user["username"], video_id)
    handler.send_json({"ok": ok})
