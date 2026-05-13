"""Chat, session, persona, and Timechain action route handlers."""

from __future__ import annotations

import uuid
from http import HTTPStatus
from typing import Any

import marketplace

from server.config import PERSONAS
from server.llm import call_llm, classify_domain, normalize_custom_persona
from server.timechain import finalize_chat_response, sanitize_session_id


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
    if user:
        mp_entry = marketplace.get_marketplace_persona(persona_id)
        if mp_entry and marketplace.is_subscribed(user["username"], persona_id):
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
    )
    response = finalize_chat_response(
        app=app,
        message=message,
        domain=domain,
        tags=[domain, "chat-poc", persona_id],
        model=model,
        llm=llm,
        persona_name=persona["name"],
    )
    response["persona_id"] = persona_id
    handler.send_json(response)


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

