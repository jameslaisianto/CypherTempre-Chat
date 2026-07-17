"""Chat, session, persona, and Timechain action route handlers."""

from __future__ import annotations

import json
import uuid
from http import HTTPStatus
from typing import Any

import marketplace

from server.config import PERSONAS
from server.llm import call_llm, classify_domain, normalize_custom_persona
from server.timechain import finalize_chat_response, sanitize_session_id


def _capsule_shared_hits(capsule: dict[str, Any] | None, *, limit: int = 8) -> list[dict[str, Any]]:
    rings = list((capsule or {}).get("rings") or [])
    rings.sort(key=lambda r: r.get("brightness", 0), reverse=True)
    hits: list[dict[str, Any]] = []
    for ring in rings[:limit]:
        hits.append({
            "content": ring.get("content", ""),
            "domain": ring.get("domain", "?"),
            "brightness": float(ring.get("brightness", 0) or 0),
            "source_session": (capsule or {}).get("source_session", "marketplace"),
            "source_ring": ring.get("n", "?"),
        })
    return hits


def handle_chat(handler: Any, app: Any) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    username = user["username"]
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=username)
    message = str(payload.get("message", "")).strip()
    persona_id = str(payload.get("persona", "companion")).strip() or "companion"
    custom_persona = normalize_custom_persona(payload.get("customPersona"))
    if custom_persona:
        app.save_custom_persona(persona_id, custom_persona, username=username)
    persona_id = app.bind_session_persona(persona_id, username=username)
    mp_persona = None
    capsule_hits: list[dict[str, Any]] = []
    if user:
        mp_persona = app.get_created_persona(persona_id, username=user["username"])
    if user and not mp_persona:
        mp_entry = marketplace.get_marketplace_persona(persona_id)
        if mp_entry and marketplace.is_subscribed(user["username"], persona_id):
            capsule_hits = _capsule_shared_hits(mp_entry.get("capsule"))
            mp_persona = {
                "name": mp_entry.get("name", "Untitled"),
                "domain": mp_entry.get("domain", "auto"),
                "system": mp_entry.get("system", ""),
            }
    persona = mp_persona or custom_persona or app.get_custom_persona(persona_id, username=username) or PERSONAS.get(persona_id) or PERSONAS["companion"]
    requested_domain = str(payload.get("domain", "auto")).strip() or "auto"
    domain = classify_domain(message, persona, requested_domain)
    model = str(payload.get("model", app.default_model)).strip() or app.default_model
    api_key = str(payload.get("apiKey", "")).strip()
    if not message:
        handler.send_json({"ok": False, "error": "message is required"}, HTTPStatus.BAD_REQUEST)
        return

    if message.lower().startswith("/fallback"):
        parts = message.split()
        if len(parts) == 1:
            mode = app.local_fallback_mode()
            handler.send_json({
                "ok": True,
                "accepted": True,
                "content": f"Local fallback mode for this session is '{mode}'. Use /fallback chat or /fallback engineering.",
                "persona_name": persona["name"],
                "persona_id": persona_id,
                "domain": domain,
                "model": model,
                "model_used": "local-command",
            })
            return

        requested = parts[1].strip().lower()
        if requested not in {"chat", "engineering"}:
            handler.send_json({
                "ok": True,
                "accepted": True,
                "content": "Unknown fallback mode. Use /fallback chat or /fallback engineering.",
                "persona_name": persona["name"],
                "persona_id": persona_id,
                "domain": domain,
                "model": model,
                "model_used": "local-command",
            })
            return

        configured = app.configure_local_fallback_mode(requested)
        handler.send_json({
            "ok": True,
            "accepted": True,
            "content": (
                f"Local fallback mode set to '{configured.get('local_fallback_mode')}' for this session. "
                "This only affects local fallback replies when no provider answer is available."
            ),
            "persona_name": persona["name"],
            "persona_id": persona_id,
            "domain": domain,
            "model": model,
            "model_used": "local-command",
        })
        return

    shared_hits = None
    if bool(payload.get("sharedMemory")):
        shared = app.shared_recall(username, message, exclude_session=app.active_session, limit=8)
        shared_hits = shared.get("hits", [])
    if capsule_hits:
        shared_hits = capsule_hits + (shared_hits or [])

    app.reload_agent()
    llm = app.generate_llm_response(
        query=message,
        domain=domain,
        persona_id=persona_id,
        custom_persona=persona,
        model=model,
        api_key=api_key,
        provider=str(payload.get("provider", "")).strip(),
        base_url=str(payload.get("baseUrl", "")).strip() or app.base_url,
        shared_hits=shared_hits,
        poq_enabled=False if payload.get("poq") is False else None,
        username=username,
    )
    llm["username"] = username
    response = finalize_chat_response(
        app=app,
        message=message,
        domain=domain,
        tags=[domain, "chat", persona_id],
        model=model,
        llm=llm,
        persona_name=persona["name"],
    )
    response["persona_id"] = persona_id
    response["trust"] = app.trust_status(username)
    handler.send_json(response)


def handle_chat_stream(handler: Any, app: Any) -> None:
    """SSE chat: token events while generating, then a final sealed result."""
    try:
        user = marketplace.require_auth(dict(handler.headers))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    username = user["username"]
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=username)
    message = str(payload.get("message", "")).strip()
    if not message:
        handler.send_json({"ok": False, "error": "message is required"}, HTTPStatus.BAD_REQUEST)
        return
    if message.lower().startswith("/fallback"):
        handle_chat(handler, app)
        return

    persona_id = str(payload.get("persona", "companion")).strip() or "companion"
    custom_persona = normalize_custom_persona(payload.get("customPersona"))
    if custom_persona:
        app.save_custom_persona(persona_id, custom_persona, username=username)
    persona_id = app.bind_session_persona(persona_id, username=username)
    mp_persona = None
    capsule_hits: list[dict[str, Any]] = []
    if user:
        mp_persona = app.get_created_persona(persona_id, username=user["username"])
    if user and not mp_persona:
        mp_entry = marketplace.get_marketplace_persona(persona_id)
        if mp_entry and marketplace.is_subscribed(user["username"], persona_id):
            capsule_hits = _capsule_shared_hits(mp_entry.get("capsule"))
            mp_persona = {
                "name": mp_entry.get("name", "Untitled"),
                "domain": mp_entry.get("domain", "auto"),
                "system": mp_entry.get("system", ""),
            }
    persona = mp_persona or custom_persona or app.get_custom_persona(persona_id, username=username) or PERSONAS.get(persona_id) or PERSONAS["companion"]
    requested_domain = str(payload.get("domain", "auto")).strip() or "auto"
    domain = classify_domain(message, persona, requested_domain)
    model = str(payload.get("model", app.default_model)).strip() or app.default_model
    api_key = str(payload.get("apiKey", "")).strip()

    shared_hits = None
    if bool(payload.get("sharedMemory")):
        shared = app.shared_recall(username, message, exclude_session=app.active_session, limit=8)
        shared_hits = shared.get("hits", [])
    if capsule_hits:
        shared_hits = capsule_hits + (shared_hits or [])

    def emit(event: str, data: dict[str, Any]) -> None:
        payload_bytes = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")
        handler.wfile.write(payload_bytes)
        handler.wfile.flush()

    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
    handler.send_header("Cache-Control", "no-cache")
    handler.send_header("Connection", "keep-alive")
    handler.send_header("X-Accel-Buffering", "no")
    handler.end_headers()

    try:
        emit("meta", {
            "persona_id": persona_id,
            "persona_name": persona["name"],
            "domain": domain,
            "model": model,
            "session": app.active_session,
        })

        def on_token(piece: str) -> None:
            emit("token", {"text": piece})

        app.reload_agent()
        llm = app.generate_llm_response(
            query=message,
            domain=domain,
            persona_id=persona_id,
            custom_persona=persona,
            model=model,
            api_key=api_key,
            provider=str(payload.get("provider", "")).strip(),
            base_url=str(payload.get("baseUrl", "")).strip() or app.base_url,
            shared_hits=shared_hits,
            poq_enabled=False if payload.get("poq") is False else None,
            username=username,
            stream=True,
            on_token=on_token,
        )
        llm["username"] = username
        if llm.get("content") and not llm.get("streamed"):
            # Non-stream fallback path still delivers content for progressive UI.
            emit("token", {"text": str(llm.get("content") or "")})
        response = finalize_chat_response(
            app=app,
            message=message,
            domain=domain,
            tags=[domain, "chat", persona_id],
            model=model,
            llm=llm,
            persona_name=persona["name"],
        )
        response["persona_id"] = persona_id
        response["trust"] = app.trust_status(username)
        emit("final", response)
    except Exception as exc:
        emit("error", {"ok": False, "error": str(exc), "type": type(exc).__name__})


def handle_recall(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    query = str(payload.get("query", "")).strip()
    domain = str(payload.get("domain", "")).strip() or None
    limit = int(payload.get("limit", 12))
    if not query:
        handler.send_json({"ok": False, "error": "query is required"}, HTTPStatus.BAD_REQUEST)
        return

    recall = app.recall(query, domain=domain, limit=limit)
    handler.send_json({"ok": True, **recall})


def handle_memory_action(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    memory_id = str(payload.get("id", "")).strip()
    action = str(payload.get("action", "")).strip().lower()
    if not memory_id or not action:
        handler.send_json({"ok": False, "error": "id and action are required"}, HTTPStatus.BAD_REQUEST)
        return
    try:
        memory = app.update_memory_status(memory_id, action, payload.get("memory") if isinstance(payload.get("memory"), dict) else {})
    except KeyError:
        handler.send_json({"ok": False, "error": f"Unknown memory: {memory_id}"}, HTTPStatus.NOT_FOUND)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, "memory": memory, **app.list_memories()})


def handle_reset(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    app.use_session(handler.query_param("session"), username=user["username"])
    result = app.reset_chain()
    handler.send_json({"ok": True, **result})


def handle_freeze(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    result = app.set_frozen(bool(payload.get("frozen")))
    handler.send_json({"ok": True, **result})


def handle_rewind(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        ring_number = int(payload.get("ring"))
        result = app.rewind_to_ring(ring_number)
    except (TypeError, ValueError) as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, **result})


def handle_dream(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        result = app.run_dream(str(payload.get("domains", "")).strip(), cycles=int(payload.get("cycles", 3)))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.CONFLICT)
        return
    except (TypeError, ValueError) as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)


def handle_overlay_set(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        result = app.set_overlay(str(payload.get("tag", "")).strip(), payload.get("weight", 1.0))
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)


def handle_memory_sync(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        result = app.memory_sync()
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)


def handle_fleet_import(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        result = app.fleet_import(payload.get("ring"), source=str(payload.get("source", "")).strip())
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.CONFLICT)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)


def handle_challenge(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        result = app.challenge(str(payload.get("indices", "")).strip(), nonce=str(payload.get("nonce", "")).strip())
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)


def handle_create_session(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    persona_id = str(payload.get("persona", "")).strip()
    custom_persona = normalize_custom_persona(payload.get("customPersona"))
    if persona_id and custom_persona:
        app.save_custom_persona(persona_id, custom_persona, username=user["username"])
    session = app.create_session(
        str(payload.get("name", "")).strip() or "New conversation",
        username=user["username"],
        persona_id=persona_id,
    )
    handler.send_json({"ok": True, "session": session, "sessions": app.list_sessions(username=user["username"])})


def handle_delete_session(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    session_id = str(payload.get("session", "")).strip()
    try:
        result = app.delete_session(session_id, username=user["username"])
    except KeyError:
        handler.send_json({"ok": False, "error": f"Unknown session: {session_id}"}, HTTPStatus.NOT_FOUND)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, **result})


def handle_rename_session(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    session_id = str(payload.get("session", "")).strip()
    name = str(payload.get("name", "")).strip()
    try:
        result = app.rename_session(session_id, name, username=user["username"])
    except KeyError:
        handler.send_json({"ok": False, "error": f"Unknown session: {session_id}"}, HTTPStatus.NOT_FOUND)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, **result})


def handle_provider_test(handler: Any, app: Any) -> None:
    payload = handler.read_json()
    model = str(payload.get("model", app.default_model)).strip() or app.default_model
    api_key = str(payload.get("apiKey", "")).strip() or app.api_key
    provider = str(payload.get("provider", "")).strip() or app.provider
    result = call_llm(
        provider=provider,
        api_key=api_key,
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly: ok"}],
        timeout=min(app.timeout, 20.0),
        base_url=str(payload.get("baseUrl", "")).strip(),
        max_tokens=16,
    )
    handler.send_json({
        "ok": True,
        "model": model,
        "model_used": result.get("model_used"),
        "content": result.get("content"),
    })


def handle_save_user_config(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    settings = {
        "provider": str(payload.get("provider", "")).strip(),
        "default_model": str(payload.get("default_model", "")).strip(),
        "base_url": str(payload.get("base_url", "")).strip(),
        "image_provider": str(payload.get("image_provider", "")).strip(),
        "image_model": str(payload.get("image_model", "")).strip(),
        "image_edit_model": str(payload.get("image_edit_model", "")).strip(),
        "image_base_url": str(payload.get("image_base_url", "")).strip(),
        "video_provider": str(payload.get("video_provider", "")).strip(),
        "video_model": str(payload.get("video_model", "")).strip(),
        "video_base_url": str(payload.get("video_base_url", "")).strip(),
        "audio_provider": str(payload.get("audio_provider", "")).strip(),
        "audio_model": str(payload.get("audio_model", "")).strip(),
        "audio_base_url": str(payload.get("audio_base_url", "")).strip(),
        "memory_autopilot": str(payload.get("memory_autopilot", "")).strip(),
        "identity_bridge": str(payload.get("identity_bridge", "")).strip(),
        "stream_replies": str(payload.get("stream_replies", "")).strip(),
    }
    saved = app.save_user_settings(user["username"], settings)
    handler.send_json({
        "ok": True,
        "settings": saved,
        "product": app.product_settings(user["username"]),
    })


def handle_export_backup(handler: Any, app: Any) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    include_media = (handler.query_param("media") or "1").strip() not in {"0", "false", "no"}
    note = (handler.query_param("note") or "").strip()
    try:
        data = app.export_user_backup(user["username"], note=note, include_media=include_media)
    except FileNotFoundError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.NOT_FOUND)
        return
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "application/zip")
    handler.send_header(
        "Content-Disposition",
        f'attachment; filename="cyphertempre-{user["username"]}-backup.zip"',
    )
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def handle_restore_backup(handler: Any, app: Any) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        handler.send_json({"ok": False, "error": "zip body required"}, HTTPStatus.BAD_REQUEST)
        return
    raw = handler.rfile.read(length)
    mode = (handler.query_param("mode") or "merge").strip().lower()
    if mode not in {"merge", "replace"}:
        mode = "merge"
    try:
        result = app.restore_user_backup(user["username"], raw, mode=mode)
    except Exception as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, **result})


def handle_session_project(handler: Any, app: Any) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    try:
        result = app.configure_session_project(
            mode=str(payload.get("mode", "project")).strip(),
            objective=str(payload.get("objective", "")).strip(),
            username=user["username"],
        )
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, **result})


def handle_task_progress(handler: Any, app: Any) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    note = str(payload.get("note", "")).strip()
    if not note:
        handler.send_json({"ok": False, "error": "note is required"}, HTTPStatus.BAD_REQUEST)
        return
    try:
        result = app.seal_task_progress(note, username=user["username"])
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, **result})


def handle_guide_explain(handler: Any, app: Any) -> None:
    payload = handler.read_json()
    topic_id = str(payload.get("topicId", "")).strip()
    model = str(payload.get("model", app.default_model)).strip() or app.default_model
    api_key = str(payload.get("apiKey", "")).strip()
    try:
        result = app.explain_guide_topic(topic_id, model=model, api_key=api_key, provider=str(payload.get("provider", "")).strip(), base_url=str(payload.get("baseUrl", "")).strip())
    except KeyError:
        handler.send_json({"ok": False, "error": f"Unknown guide topic: {topic_id}"}, HTTPStatus.NOT_FOUND)
        return
    handler.send_json({"ok": True, **result})


def handle_save_persona(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    persona_id = str(payload.get("id", "")).strip() or f"custom_{uuid.uuid4().hex[:12]}"
    persona = app.save_custom_persona(persona_id, payload.get("persona"), username=user["username"])
    handler.send_json({
        "ok": True,
        "id": sanitize_session_id(persona_id),
        "persona": persona,
        "custom_personas": app.custom_personas(username=user["username"]),
    })


def handle_delete_persona(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    persona_id = str(payload.get("id", "")).strip()
    try:
        custom_personas = app.delete_custom_persona(persona_id, username=user["username"])
    except KeyError:
        handler.send_json({"ok": False, "error": f"Unknown custom persona: {persona_id}"}, HTTPStatus.NOT_FOUND)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json({"ok": True, "id": sanitize_session_id(persona_id), "custom_personas": custom_personas})



def handle_shared_memory_recall(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    session = handler.query_param("session")
    query = handler.query_param("query")
    limit = int(handler.query_param("limit") or "12")
    if not query:
        handler.send_json({"ok": False, "error": "query is required"}, HTTPStatus.BAD_REQUEST)
        return
    app.use_session(session, username=user["username"])
    result = app.shared_recall(user["username"], query, exclude_session=app.active_session, limit=limit)
    handler.send_json({"ok": True, **result})


def handle_shared_memory_import(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    hit_id = str(payload.get("hitId", "")).strip()
    if not hit_id:
        handler.send_json({"ok": False, "error": "hitId is required"}, HTTPStatus.BAD_REQUEST)
        return
    try:
        result = app.import_shared_memory(hit_id, username=user["username"])
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.CONFLICT)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)


def handle_shared_memory_synthesize(handler: Any, app: Any) -> None:
    try:
        user = handler._auth_user()
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
        return
    payload = handler.read_json()
    app.use_session(str(payload.get("session", "")).strip() or handler.query_param("session"), username=user["username"])
    query = str(payload.get("query", "")).strip()
    hit_ids = payload.get("hitIds", [])
    if not isinstance(hit_ids, list):
        handler.send_json({"ok": False, "error": "hitIds must be a list"}, HTTPStatus.BAD_REQUEST)
        return
    try:
        result = app.synthesize_comprehension(query, hit_ids, username=user["username"])
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.CONFLICT)
        return
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    handler.send_json(result)
