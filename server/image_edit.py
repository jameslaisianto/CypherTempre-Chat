"""Reference-image editing — isolated from chat LLM flows and text-only generation."""

from __future__ import annotations

import base64
import json
import mimetypes
import re
import urllib.error
import urllib.request
from typing import Any

from server.config import IMAGE_PROVIDERS, clamp_surplus_image_prompt, resolve_provider_endpoint

_SURPLUS_EDIT_PROMPT_BUDGET = 1400

# Known SurplusIntelligence /v1/images/edits models (advertised via /v1/models).
# Uncensored / least-filtered models first — default edit experience is unfiltered.
SURPLUS_EDIT_MODELS: tuple[str, ...] = (
    "qwen-edit-uncensored",
    "qwen-image-2-edit",
    "qwen-image-2-pro-edit",
    "grok-imagine-edit",
    "grok-imagine-quality-edit",
    "flux-2-max-edit",
    "gpt-image-2-edit",
    "gpt-image-1-5-edit",
    "seedream-v4-edit",
    "seedream-v5-lite-edit",
    "firered-image-edit",
    "wan-2-7-pro-edit",
    "nano-banana-2-edit",
    "nano-banana-pro-edit",
    "nano-banana-2-lite-edit",
    "luma-uni-1-edit",
    "luma-uni-1-max-edit",
)

DEFAULT_SURPLUS_EDIT_MODEL = SURPLUS_EDIT_MODELS[0]

# Map common generation / base model ids onto their edit counterparts.
_SURPLUS_EDIT_MODEL_ALIASES: dict[str, str] = {
    "gpt-image-2": "gpt-image-2-edit",
    "gpt-image-1-5": "gpt-image-1-5-edit",
    "gpt-image-1.5": "gpt-image-1-5-edit",
    "flux-2-max": "flux-2-max-edit",
    "grok-imagine": "grok-imagine-edit",
    "grok-imagine-image": "grok-imagine-edit",
    "grok-imagine-quality": "grok-imagine-quality-edit",
    "seedream-v4": "seedream-v4-edit",
    "seedream-v5-lite": "seedream-v5-lite-edit",
    "firered-image": "firered-image-edit",
    "qwen-image-2": "qwen-image-2-edit",
    "qwen-image-2-pro": "qwen-image-2-pro-edit",
    "nano-banana-2": "nano-banana-2-edit",
    "nano-banana-pro": "nano-banana-pro-edit",
    "nano-banana-2-lite": "nano-banana-2-lite-edit",
    "luma-uni-1": "luma-uni-1-edit",
    "luma-uni-1-max": "luma-uni-1-max-edit",
    "wan-2-7-pro": "wan-2-7-pro-edit",
}


def looks_like_edit_model(model_id: str) -> bool:
    """True when a model id is an image-to-image / edit model rather than text-to-image."""
    lowered = (model_id or "").strip().lower()
    if not lowered:
        return False
    return (
        lowered.endswith("-edit")
        or lowered.endswith("_edit")
        or "-edit-" in lowered
        or "_edit_" in lowered
        or "image-edit" in lowered
    )


def prefer_uncensored_edit_models(model_ids: list[str] | tuple[str, ...]) -> list[str]:
    """Stable-sort so uncensored / least-filtered edit models appear first."""

    def rank(model_id: str) -> tuple[int, str]:
        lowered = (model_id or "").lower()
        if "uncensored" in lowered:
            return (0, lowered)
        if any(token in lowered for token in ("qwen-edit", "lustify", "venice", "firered")):
            return (1, lowered)
        if "grok-imagine" in lowered or "flux" in lowered:
            return (2, lowered)
        return (3, lowered)

    return sorted((m for m in model_ids if m), key=rank)


def normalize_surplus_edit_model(model: str) -> str:
    """Coerce generation / base model names onto Surplus edit models when possible."""
    raw = (model or "").strip()
    if not raw:
        return DEFAULT_SURPLUS_EDIT_MODEL
    if looks_like_edit_model(raw):
        return raw
    lowered = raw.lower()
    if lowered in _SURPLUS_EDIT_MODEL_ALIASES:
        return _SURPLUS_EDIT_MODEL_ALIASES[lowered]
    # Prefer known catalog match by stripping trailing generation tokens.
    for base, edit in _SURPLUS_EDIT_MODEL_ALIASES.items():
        if lowered == base or lowered.startswith(base + "-") or lowered.startswith(base + "_"):
            return edit
    candidate = f"{raw}-edit"
    if candidate in SURPLUS_EDIT_MODELS:
        return candidate
    return raw


def build_edit_instruction(user_prompt: str, *, provider: str = "", native_i2i: bool = False) -> str:
    """Build the text instruction sent with a source image.

    Native I2I (Surplus /images/edits and similar): pass the user's request through
    uncensored — no safety rewrites, no wardrobe/identity soft-filters, no policy text.

    Chat-modality edit models: light edit framing only (still no content filtering).
    """
    prompt = str(user_prompt or "").strip()
    use_native = native_i2i or provider == "surplusintelligence"
    if use_native:
        if not prompt:
            prompt = "Improve clarity and detail while keeping the subject and composition."
        if provider == "surplusintelligence":
            return clamp_surplus_image_prompt(prompt, limit=_SURPLUS_EDIT_PROMPT_BUDGET)
        return prompt

    if not prompt:
        return "Apply the requested edit to the source image. Follow the user's intent exactly."
    # No policy/safety language — only operational framing for chat-modality models.
    return f"Edit the source image according to this request: {prompt}"


def _provider_config(provider: str, base_url: str) -> dict[str, Any]:
    config = IMAGE_PROVIDERS.get(provider, IMAGE_PROVIDERS.get("openrouter", {}))
    if provider == "other":
        config = {"url": "", "needs_referer": False, "needs_title": False, "label": "Custom"}
    provider_url = base_url or config.get("url", "")
    return {
        **config,
        "provider_url": provider_url,
        "api_root": _api_root(provider_url),
    }


def _api_root(provider_url: str) -> str:
    api_root = (provider_url or "").strip().rstrip("/")
    for suffix in (
        "/chat/completions",
        "/audio/speech",
        "/images/generations",
        "/images/edits",
    ):
        if api_root.endswith(suffix):
            api_root = api_root[: -len(suffix)].rstrip("/")
    return api_root


def _request_headers(config: dict[str, Any], provider: str, api_key: str, *, json_body: bool = True) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    if json_body:
        headers["Content-Type"] = "application/json"
    if config.get("needs_referer"):
        headers["HTTP-Referer"] = "http://127.0.0.1:8765"
    if config.get("needs_title"):
        headers["X-Title"] = "CypherTempre"
    return headers


def _extract_image_parts(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    for message in messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                parts.append(part)
    return parts


def _extract_user_prompt(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(str(part.get("text", "")))
    return "\n".join(part.strip() for part in parts if part.strip())


def _image_url_from_part(part: dict[str, Any]) -> str:
    """Normalize an OpenAI-style image_url content part into a usable image_url string."""
    image_url = part.get("image_url")
    if isinstance(image_url, dict):
        return str(image_url.get("url") or "").strip()
    if isinstance(image_url, str):
        return image_url.strip()
    return str(part.get("url") or "").strip()


def _source_image_urls(messages: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for part in _extract_image_parts(messages):
        url = _image_url_from_part(part)
        if url:
            urls.append(url)
    return urls


def _decode_data_url(data_url: str) -> tuple[bytes, str]:
    """Return (bytes, mime) from a data: URL."""
    if not data_url.startswith("data:"):
        raise ValueError("Not a data URL")
    header, _, payload = data_url.partition(",")
    mime = "image/png"
    if header.startswith("data:") and ";" in header:
        mime = header[5:].split(";", 1)[0] or mime
    raw = base64.b64decode(payload)
    return raw, mime


def _build_native_edit_messages(messages: list[dict[str, Any]], *, provider: str = "") -> list[dict[str, Any]]:
    image_parts = _extract_image_parts(messages)
    if not image_parts:
        raise RuntimeError("Source image is required for image editing.")
    user_prompt = _extract_user_prompt(messages)
    return [{
        "role": "user",
        "content": [
            *image_parts,
            {"type": "text", "text": build_edit_instruction(user_prompt, provider=provider)},
        ],
    }]


def _parse_image_response(body: dict[str, Any], *, timeout: float, label: str) -> list[str]:
    results: list[str] = []

    def append_image_value(value: Any) -> None:
        if not value:
            return
        if isinstance(value, dict):
            for key in ("b64_json", "b64", "base64", "data", "url", "image_url", "imageUrl", "image"):
                before = len(results)
                append_image_value(value.get(key))
                if len(results) > before:
                    break
            return
        if isinstance(value, list):
            for item in value:
                append_image_value(item)
            return
        text = str(value).strip()
        if not text:
            return
        if text.startswith("data:image"):
            results.append(text.split(",", 1)[1] if "," in text else text)
        elif text.startswith("https://") or text.startswith("http://"):
            request = urllib.request.Request(text, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    results.append(base64.b64encode(response.read()).decode("ascii"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"{label} image download HTTP {exc.code}: {detail}") from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(f"{label} image download failed: {exc.reason}") from exc
        else:
            # Assume raw base64.
            results.append(text)

    choices = body.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        for img in message.get("images") or []:
            append_image_value(img)
        if not results:
            content = message.get("content")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        append_image_value(part)
            elif isinstance(content, str) and content.strip().startswith("data:image"):
                append_image_value(content)

    if not results:
        for item in body.get("data") or []:
            append_image_value(item)

    if not results:
        append_image_value(body.get("url") or body.get("image_url") or body.get("imageUrl") or body.get("image"))

    if not results:
        append_image_value(body.get("output") or body.get("result") or body.get("images"))

    return results


def _post_json(
    *,
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: float,
    label: str,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or parsed.get("message") or detail
        except json.JSONDecodeError:
            message = detail
        raise RuntimeError(f"{label} HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{label} request failed: {exc.reason}") from exc


def _post_multipart(
    *,
    url: str,
    fields: dict[str, str],
    files: list[tuple[str, str, bytes, str]],
    headers: dict[str, str],
    timeout: float,
    label: str,
) -> dict[str, Any]:
    """Minimal multipart/form-data POST for OpenAI-style image edits."""
    boundary = "----CypherTempreBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")
    for field_name, filename, content, mime in files:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode("utf-8")
        )
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
        body.extend(content)
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req_headers = dict(headers)
    req_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    request = urllib.request.Request(url, data=bytes(body), headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or parsed.get("message") or detail
        except json.JSONDecodeError:
            message = detail
        raise RuntimeError(f"{label} HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{label} request failed: {exc.reason}") from exc


def _size_for_aspect(aspect_ratio: str, image_size: str) -> str:
    if re.fullmatch(r"\d+x\d+", image_size or ""):
        return image_size
    size_map = {
        "1:1": "1024x1024",
        "16:9": "1536x1024",
        "4:3": "1536x1024",
        "9:16": "1024x1536",
    }
    return size_map.get(aspect_ratio or "", "")


def _native_image_edit(
    *,
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: float,
    base_url: str,
    aspect_ratio: str,
    image_size: str,
) -> list[str]:
    """Grok Imagine-style edit: source image + instruction via chat/completions."""
    config = _provider_config(provider, base_url)
    url = resolve_provider_endpoint(config["provider_url"], "chat/completions")
    if not url:
        raise RuntimeError(f"No URL configured for image edit provider: {provider}")

    payload: dict[str, Any] = {
        "model": model or config.get("default_model", ""),
        "messages": _build_native_edit_messages(messages, provider=provider),
        "modalities": ["image", "text"],
    }
    image_config: dict[str, Any] = {}
    if aspect_ratio:
        image_config["aspect_ratio"] = aspect_ratio
    if image_size:
        image_config["image_size"] = image_size
    if image_config:
        payload["image_config"] = image_config

    body = _post_json(
        url=url,
        payload=payload,
        headers=_request_headers(config, provider, api_key),
        timeout=timeout,
        label=config.get("label", provider),
    )
    images = _parse_image_response(body, timeout=timeout, label=config.get("label", provider))
    if not images:
        raise RuntimeError(f"{config.get('label', provider)} returned no edited image.")
    return images


def _surplus_payload_variants(
    *,
    model: str,
    prompt: str,
    source_urls: list[str],
    aspect_ratio: str,
    image_size: str,
) -> list[dict[str, Any]]:
    """Ordered Surplus /images/edits JSON payload strategies."""
    size = _size_for_aspect(aspect_ratio, image_size)
    primary = source_urls[0]
    base: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
    }
    variants: list[dict[str, Any]] = []

    # 1) Docs-preferred: image_url (+ optional size)
    v1 = {**base, "image_url": primary}
    if size:
        v1["size"] = size
    variants.append(v1)

    # 2) image_url without size (let model preserve source dimensions)
    if size:
        variants.append({**base, "image_url": primary})

    # 3) input_images array (multi-ref friendly)
    v3 = {**base, "input_images": source_urls, "image_url": primary}
    if size:
        v3["size"] = size
    variants.append(v3)

    # 4) response_format url (some gateways only return URLs cleanly)
    variants.append({**base, "image_url": primary, "response_format": "url"})

    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for payload in variants:
        key = json.dumps(payload, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(payload)
    return unique


def _surplus_multipart_edit(
    *,
    url: str,
    model: str,
    prompt: str,
    source_urls: list[str],
    size: str,
    headers: dict[str, str],
    timeout: float,
    label: str,
) -> dict[str, Any]:
    """Fallback: multipart image upload when JSON image_url is rejected."""
    data_url = next((u for u in source_urls if u.startswith("data:")), "")
    if not data_url:
        raise RuntimeError("Multipart edit requires a local data-URL source image.")
    raw, mime = _decode_data_url(data_url)
    ext = mimetypes.guess_extension(mime) or ".png"
    fields = {
        "model": model,
        "prompt": prompt,
        "n": "1",
        "response_format": "b64_json",
    }
    if size:
        fields["size"] = size
    return _post_multipart(
        url=url,
        fields=fields,
        files=[("image", f"source{ext}", raw, mime)],
        headers=headers,
        timeout=timeout,
        label=label,
    )


def _friendly_surplus_error(message: str, *, model: str) -> str:
    lowered = (message or "").lower()
    if "payment" in lowered or "402" in lowered or "x402" in lowered:
        return (
            f"{message} "
            "Surplus billing is required for image edits — top up or complete SIWE settlement, then retry."
        )
    if "model" in lowered and ("not found" in lowered or "invalid" in lowered or "unsupported" in lowered):
        return (
            f"{message} "
            f"Pick a Surplus edit model such as {SURPLUS_EDIT_MODELS[0]} or grok-imagine-edit "
            "(not a /images/generations model)."
        )
    if "image" in lowered and any(tok in lowered for tok in ("required", "missing", "invalid", "format", "decode")):
        return (
            f"{message} "
            "Upload a clear PNG/JPG source image. Large files are auto-compressed before send."
        )
    if "generations" in lowered:
        return (
            f"{message} "
            "Image editing uses POST /v1/images/edits with an input image, not /v1/images/generations."
        )
    if model and not looks_like_edit_model(model):
        return (
            f"{message} "
            f"Current model '{model}' may not be an edit model — try {normalize_surplus_edit_model(model)}."
        )
    return message


def _surplus_native_image_edit(
    *,
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: float,
    base_url: str,
    aspect_ratio: str,
    image_size: str,
) -> list[str]:
    """SurplusIntelligence native edit via POST /v1/images/edits.

    Accepts JSON ``image_url`` (data URL or https URL), ``input_images``, or multipart
    image upload. Do not use /v1/images/generations for edits.
    """
    config = _provider_config(provider, base_url)
    url = resolve_provider_endpoint(config["api_root"], "images/edits")
    if not url:
        raise RuntimeError("No URL configured for SurplusIntelligence image edits.")

    source_urls = _source_image_urls(messages)
    if not source_urls:
        raise RuntimeError(
            "Source image is required for image editing. "
            "Use POST /v1/images/edits with an input image (not /v1/images/generations)."
        )

    # Trust the handler-prepared text (native prepare / raw bypass). Only clamp length.
    # Re-wrapping here would fight ChatGPT/Grok-style short conversational edits.
    prompt = clamp_surplus_image_prompt(
        _extract_user_prompt(messages),
        limit=_SURPLUS_EDIT_PROMPT_BUDGET,
    )
    if not prompt:
        raise RuntimeError("Edit prompt is required.")

    edit_model = normalize_surplus_edit_model(model)
    label = config.get("label", provider)
    headers = _request_headers(config, provider, api_key)
    last_error: Exception | None = None

    for payload in _surplus_payload_variants(
        model=edit_model,
        prompt=prompt,
        source_urls=source_urls,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
    ):
        try:
            body = _post_json(
                url=url,
                payload=payload,
                headers=headers,
                timeout=timeout,
                label=label,
            )
            images = _parse_image_response(body, timeout=timeout, label=label)
            if images:
                return images
            last_error = RuntimeError(f"{label} returned no edited image from /images/edits.")
        except RuntimeError as exc:
            last_error = exc
            # Hard stop on auth/payment — retrying the same wallet error is useless.
            msg = str(exc).lower()
            if any(tok in msg for tok in ("401", "403", "402", "payment", "unauthorized", "forbidden", "api key")):
                raise RuntimeError(_friendly_surplus_error(str(exc), model=edit_model)) from exc
            continue

    # Final fallback: multipart upload for gateways that reject JSON data URLs.
    try:
        body = _surplus_multipart_edit(
            url=url,
            model=edit_model,
            prompt=prompt,
            source_urls=source_urls,
            size=_size_for_aspect(aspect_ratio, image_size),
            headers=_request_headers(config, provider, api_key, json_body=False),
            timeout=timeout,
            label=label,
        )
        images = _parse_image_response(body, timeout=timeout, label=label)
        if images:
            return images
    except Exception as exc:  # noqa: BLE001 — fall through to last JSON error
        last_error = last_error or exc

    if last_error:
        raise RuntimeError(_friendly_surplus_error(str(last_error), model=edit_model)) from last_error
    raise RuntimeError(f"{label} returned no edited image from /images/edits.")


def call_image_edit(
    *,
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: float,
    base_url: str = "",
    aspect_ratio: str = "",
    image_size: str = "",
) -> list[str]:
    """Edit an image only through a native reference-image path."""
    placeholder_keys = {
        "YOUR_API_KEY",
        "YOUR_MORPHEUS_API_KEY",
        "YOUR_OPENROUTER_API_KEY",
        "sk-or-your-key-here",
        "sk-or-your-real-key",
    }
    if api_key in placeholder_keys:
        raise RuntimeError("API key is still the example placeholder.")

    if provider == "surplusintelligence":
        return _surplus_native_image_edit(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=timeout,
            base_url=base_url,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        )

    return _native_image_edit(
        provider=provider,
        api_key=api_key,
        model=model,
        messages=messages,
        timeout=timeout,
        base_url=base_url,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
    )


def call_image_redefine(
    *,
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: float,
    base_url: str = "",
    aspect_ratio: str = "",
    image_size: str = "",
) -> list[str]:
    """Create a new interpretation from a source image via native image-to-image edit."""
    return call_image_edit(
        provider=provider,
        api_key=api_key,
        model=model,
        messages=messages,
        timeout=timeout,
        base_url=base_url,
        aspect_ratio=aspect_ratio,
        image_size=image_size,
    )
