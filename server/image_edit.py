"""Reference-image editing — isolated from chat LLM flows and text-only generation."""

from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.request
from typing import Any

from server.config import IMAGE_PROVIDERS, clamp_surplus_image_prompt, resolve_provider_endpoint
from server.llm import call_llm, list_provider_models

_EDIT_IDENTITY_RULES = (
    "Preserve exact facial features, identity, pose, wardrobe, lighting, and composition "
    "unless the request explicitly changes them. Apply only the requested change."
)

_FALLBACK_VISION_PROMPT = (
    "Analyze the supplied image and write one concise image-generation prompt that preserves "
    "subject identity, facial features, pose, colors, and important details while applying "
    "this change: {prompt}. Return only the final prompt. Maximum 1400 characters."
)

_SURPLUS_VISION_USER_PROMPT_BUDGET = 500


def build_edit_instruction(user_prompt: str, *, provider: str = "") -> str:
    """Wrap the user's edit request with identity-preservation constraints."""
    prompt = str(user_prompt or "").strip()
    if provider == "surplusintelligence":
        prompt = clamp_surplus_image_prompt(prompt, limit=_SURPLUS_VISION_USER_PROMPT_BUDGET)
    if not prompt:
        instruction = _EDIT_IDENTITY_RULES
    else:
        instruction = f"Edit the source image. Change: {prompt}. {_EDIT_IDENTITY_RULES}"
    if provider == "surplusintelligence":
        return clamp_surplus_image_prompt(instruction)
    return instruction


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
    for suffix in ("/chat/completions", "/audio/speech", "/images/generations"):
        if api_root.endswith(suffix):
            api_root = api_root[: -len(suffix)].rstrip("/")
    return api_root


def _request_headers(config: dict[str, Any], provider: str, api_key: str) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if config.get("needs_referer"):
        headers["HTTP-Referer"] = "http://127.0.0.1:8765"
    if config.get("needs_title"):
        headers["X-Title"] = "CypherTempre Chat PoC"
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
            for key in ("b64_json", "data", "url", "image_url", "imageUrl"):
                before = len(results)
                append_image_value(value.get(key))
                if len(results) > before:
                    break
            return
        text = str(value).strip()
        if not text:
            return
        if text.startswith("data:image"):
            results.append(text.split(",", 1)[1] if "," in text else text)
        elif text.startswith("https://"):
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
            results.append(text)

    choices = body.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        for img in message.get("images") or []:
            append_image_value(img)
        if not results:
            content = (message.get("content") or "").strip()
            if content.startswith("data:image"):
                append_image_value(content)

    if not results:
        for item in body.get("data") or []:
            append_image_value(item)

    if not results:
        append_image_value(body.get("url") or body.get("image_url") or body.get("imageUrl"))

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


def _surplus_regenerate_fallback(
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
    """Last-resort SurplusIntelligence path when native multimodal edit is unavailable."""
    config = _provider_config(provider, base_url)
    user_prompt = clamp_surplus_image_prompt(
        _extract_user_prompt(messages),
        limit=_SURPLUS_VISION_USER_PROMPT_BUDGET,
    )
    image_parts = _extract_image_parts(messages)
    if not image_parts:
        raise RuntimeError("Source image is required for image editing.")

    catalog = list_provider_models(
        provider=provider,
        base_url=config["provider_url"],
        api_key=api_key,
        timeout=min(timeout, 20.0),
    )
    vision_models = catalog.get("vision") or []
    if not vision_models:
        raise RuntimeError("SurplusIntelligence returned no vision model for source-aware image editing.")
    vision_ids = [item["id"] for item in vision_models]
    preferred_vision_ids = ("gemini-2.5-flash", "gpt-5.4-nano", "gemma-4-uncensored")
    vision_model = next(
        (candidate for candidate in preferred_vision_ids if candidate in vision_ids),
        vision_ids[0],
    )
    analysis = call_llm(
        provider=provider,
        api_key=api_key,
        model=vision_model,
        messages=[{
            "role": "user",
            "content": [
                *image_parts,
                {"type": "text", "text": _FALLBACK_VISION_PROMPT.format(prompt=user_prompt)},
            ],
        }],
        timeout=timeout,
        base_url=config["provider_url"],
        max_tokens=900,
    )
    prompt = clamp_surplus_image_prompt(str(analysis.get("content") or "").strip())
    if not prompt:
        raise RuntimeError("SurplusIntelligence vision analysis returned an empty edit prompt.")

    size_map = {
        "1:1": "1024x1024",
        "16:9": "1536x1024",
        "4:3": "1536x1024",
        "9:16": "1024x1536",
    }
    url = resolve_provider_endpoint(config["api_root"], "images/generations")
    payload = {
        "model": model or config.get("default_model", ""),
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "size": image_size if re.fullmatch(r"\d+x\d+", image_size or "") else size_map.get(aspect_ratio, "1024x1024"),
    }
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
        raise RuntimeError(
            "SurplusIntelligence does not expose a native image-edit endpoint. "
            "Use Redefine for a new interpretation, or configure an image provider/model "
            "that accepts the source image as edit input."
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
    """Create a new interpretation from a source image.

    SurplusIntelligence has generation but no native edit endpoint, so Redefine is
    the explicit place where describe-then-regenerate behavior is allowed.
    """
    if provider == "surplusintelligence":
        return _surplus_regenerate_fallback(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=messages,
            timeout=timeout,
            base_url=base_url,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        )
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
