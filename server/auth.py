"""Authentication route handlers."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any

import marketplace


def handle_auth_me(handler: Any) -> None:
    headers = dict(handler.headers)
    token = marketplace.get_cookie_token(headers) or headers.get("X-Auth-Token", "")
    user = marketplace.get_auth_user(token)
    handler.send_json({"ok": True, "user": user})


def handle_auth_register(handler: Any) -> None:
    payload = handler.read_json()
    try:
        result = marketplace.create_user(
            str(payload.get("username", "")).strip(),
            str(payload.get("display_name", "")).strip(),
            str(payload.get("password", "")).strip(),
            str(payload.get("role", "subscriber")).strip(),
        )
        token = marketplace.create_auth_session(result["username"])
        handler.send_response(HTTPStatus.OK)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Set-Cookie", f"ct_auth={token}; HttpOnly; Path=/; Max-Age={60*60*24*7}; SameSite=Strict")
        handler.end_headers()
        handler.wfile.write(json.dumps({"ok": True, "user": result, "token": token}).encode("utf-8"))
    except ValueError as exc:
        handler.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)


def handle_auth_login(handler: Any) -> None:
    payload = handler.read_json()
    user = marketplace.authenticate_user(
        str(payload.get("username", "")).strip(),
        str(payload.get("password", "")).strip(),
    )
    if not user:
        handler.send_json({"ok": False, "error": "Invalid credentials."}, HTTPStatus.UNAUTHORIZED)
        return
    token = marketplace.create_auth_session(user["username"])
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Set-Cookie", f"ct_auth={token}; HttpOnly; Path=/; Max-Age={60*60*24*7}; SameSite=Strict")
    handler.end_headers()
    handler.wfile.write(json.dumps({"ok": True, "user": user, "token": token}).encode("utf-8"))


def handle_auth_logout(handler: Any) -> None:
    token = marketplace.get_cookie_token(dict(handler.headers))
    marketplace.delete_auth_session(token)
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Set-Cookie", "ct_auth=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict")
    handler.end_headers()
    handler.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
