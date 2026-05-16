"""Marketplace and creator route handlers."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

import marketplace


def handle_catalog(handler: Any) -> None:
    catalog = marketplace.get_catalog()
    user = marketplace.get_auth_user(marketplace.get_auth_token(dict(handler.headers)))
    subs = marketplace.get_subscriptions(user["username"]) if user else []
    sub_ids = {s["persona_id"] for s in subs}
    for entry in catalog:
        entry["is_subscribed"] = entry["persona_id"] in sub_ids
    handler.send_json({"ok": True, "personas": [p for p in catalog if p.get("status") == "published"]})


def handle_persona_detail(handler: Any, persona_id: str) -> None:
    entry = marketplace.get_marketplace_persona(persona_id)
    if not entry:
        handler.send_error(HTTPStatus.NOT_FOUND, "Not found")
        return
    user = marketplace.get_auth_user(marketplace.get_auth_token(dict(handler.headers)))
    entry["is_subscribed"] = marketplace.is_subscribed(user["username"], persona_id) if user else False
    handler.send_json({"ok": True, "persona": entry})


def handle_subscriptions(handler: Any) -> None:
    user = marketplace.require_auth(dict(handler.headers))
    subs = marketplace.get_subscriptions(user["username"])
    handler.send_json({"ok": True, "subscriptions": subs})


def handle_creator_personas(handler: Any) -> None:
    user = marketplace.require_role(dict(handler.headers), "creator")
    created = marketplace.list_created_personas(user["username"])
    handler.send_json({"ok": True, "personas": created})


def handle_creator_persona_detail(handler: Any, persona_id: str) -> None:
    user = marketplace.require_role(dict(handler.headers), "creator")
    entry = marketplace.get_created_persona(user["username"], persona_id)
    if not entry:
        handler.send_error(HTTPStatus.NOT_FOUND, "Not found")
        return
    handler.send_json({"ok": True, "persona": entry})


def handle_subscribe(handler: Any, persona_id: str) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
        result = marketplace.subscribe(user["username"], persona_id)
        handler.send_json({"ok": True, **result})
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)


def handle_unsubscribe(handler: Any, persona_id: str) -> None:
    try:
        user = marketplace.require_auth(dict(handler.headers))
        result = marketplace.unsubscribe(user["username"], persona_id)
        handler.send_json({"ok": True, **result})
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)


def handle_creator_create(handler: Any) -> None:
    try:
        user = marketplace.require_role(dict(handler.headers), "creator")
        payload = handler.read_json()
        data = payload.get("persona", {})
        persona_id = str(payload.get("id", "")).strip() or None
        result = marketplace.save_created_persona(user["username"], persona_id, data)
        handler.send_json({"ok": True, "persona": result})
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)


def handle_creator_distill(handler: Any, app: Any, persona_id: str) -> None:
    try:
        user = marketplace.require_role(dict(handler.headers), "creator")
        payload = handler.read_json()
        source_session = str(payload.get("sourceSession") or payload.get("source_session") or "").strip() or None
        capsule = marketplace.distill_persona(user["username"], persona_id, app.timechain, source_session=source_session)
        handler.send_json({"ok": True, "capsule": capsule})
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
    except KeyError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.NOT_FOUND)


def handle_creator_publish(handler: Any, persona_id: str) -> None:
    try:
        user = marketplace.require_role(dict(handler.headers), "creator")
        payload = handler.read_json()
        result = marketplace.publish_persona(user["username"], persona_id, payload.get("price"))
        handler.send_json({"ok": True, "persona": result})
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
    except KeyError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.NOT_FOUND)


def handle_creator_delete(handler: Any, persona_id: str) -> None:
    try:
        user = marketplace.require_role(dict(handler.headers), "creator")
        marketplace.delete_created_persona(user["username"], persona_id)
        handler.send_json({"ok": True, "deleted": persona_id})
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
    except PermissionError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
