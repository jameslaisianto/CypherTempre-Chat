#!/usr/bin/env python3
"""Thin HTTP server â€” route dispatch, request handling, argument parsing, main entry point."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import sys
import traceback
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

import marketplace
from server import auth, chat, imagegen, videogen, audiogen
from server import marketplace as marketplace_routes

from server.config import (
    DEFAULT_MODEL, DEFAULT_PROVIDER, PROVIDERS, IMAGE_PROVIDERS, VIDEO_PROVIDERS, AUDIO_PROVIDERS, PERSONAS,
    DEFAULT_TIMECHAIN_PATH, DEFAULT_ENV_PATH,
    DEFAULT_POQ_ENABLED, DEFAULT_POQ_MIN_SCORE, DEFAULT_POQ_MAX_RETRIES,
    DEFAULT_POQ_OVERFITTING_CHECK,
    default_provider_url,
)
from server.html import HTML_TEMPLATE
from server.ui import UI_JS
from server.timechain import App
from server.timechain import (
    custom_personas_path,
    env_value,
    guide_topics_payload,
    load_all_public_custom_personas,
    load_local_env,
    sanitize_session_id,
)
from server.llm import list_provider_models, safe_persona_metadata, serialize_history

# Compose the full HTML page from template and JS
HTML = HTML_TEMPLATE.replace("{ui_js}", UI_JS)

MANIFEST_JSON = json.dumps({
    "name": "CypherTempre Chat",
    "short_name": "CypherTempre",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0b0c0b",
    "theme_color": "#0b0c0b",
    "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml"}]
}, indent=2)

SW_JS = (
    "const CACHE_NAME = 'cyphertempre-v4';\\n"
    "const URLS_TO_CACHE = ['/','/manifest.json','/icon.svg'];\\n"
    "self.addEventListener('install', e => {\\n"
    "  self.skipWaiting();\\n"
    "  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(URLS_TO_CACHE)));\\n"
    "});\\n"
    "self.addEventListener('activate', e => {\\n"
    "  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))).then(() => self.clients.claim()));\\n"
    "});\\n"
    "self.addEventListener('fetch', e => {\\n"
    "  if (e.request.mode === 'navigate') { e.respondWith(fetch(e.request).catch(() => caches.match('/'))); return; }\\n"
    "  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));\\n"
    "});\\n"
)

ICON_SVG = (
    '<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\">'
    '<rect width=\"100\" height=\"100\" rx=\"20\" fill=\"#0b0c0b\"/>'
    '<text x=\"50\" y=\"68\" font-size=\"52\" text-anchor=\"middle\" fill=\"#d6b36a\" font-family=\"ui-sans-serif,system-ui,sans-serif\">C</text>'
    '</svg>'
)

def with_runtime_metadata(personas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        key: {**value, **safe_persona_metadata(key, value)}
        for key, value in (personas or {}).items()
    }


def resolve_model_discovery_credentials(
    app: App,
    provider: str,
    *,
    api_key_override: str = "",
    base_url_override: str = "",
) -> tuple[str, str]:
    """Pick the API key and base URL used to discover models for a provider.

    Image/video/audio providers must use their modality-specific credentials so the
    catalog matches what ImageGen and other studios can actually call.
    """
    provider = (provider or app.provider).strip().lower()
    api_key = (api_key_override or "").strip()
    base_url = (base_url_override or "").strip()

    if provider in IMAGE_PROVIDERS:
        base_url = base_url or app.image_base_url or IMAGE_PROVIDERS[provider].get("url", "")
        api_key = api_key or app.image_api_key or app.api_key
    elif provider in VIDEO_PROVIDERS:
        base_url = base_url or app.video_base_url or VIDEO_PROVIDERS[provider].get("url", "")
        api_key = api_key or app.video_api_key or app.api_key
    elif provider in AUDIO_PROVIDERS:
        base_url = base_url or app.audio_base_url or AUDIO_PROVIDERS[provider].get("url", "")
        api_key = api_key or app.audio_api_key or app.api_key
    elif provider == app.provider:
        base_url = base_url or app.base_url or default_provider_url(provider)
        api_key = api_key or app.api_key
    else:
        base_url = base_url or default_provider_url(provider)
        api_key = api_key or app.api_key
    return api_key, base_url


def make_handler(app: App) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "CypherTempreChatPoC/0.2"

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"{self.address_string()} - {fmt % args}")

        def _auth_user(self) -> dict[str, Any]:
            user = marketplace.require_auth(dict(self.headers))
            return user

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            try:
                if path == "/":
                    self.send_html(HTML)
                    return
                if path == "/api/config":
                    user = marketplace.get_auth_user(marketplace.get_cookie_token(dict(self.headers)))
                    mp_personas = {}
                    custom_personas = {}
                    public_personas = {}
                    creator_personas = {}
                    user_settings = {}
                    if user:
                        subs = marketplace.get_subscriptions(user["username"])
                        for sub in subs:
                            entry = marketplace.get_marketplace_persona(sub["persona_id"])
                            if entry:
                                mp_personas[sub["persona_id"]] = {
                                    "name": entry.get("name", "Untitled"),
                                    "domain": entry.get("domain", "auto"),
                                    "system": entry.get("system", ""),
                                }
                        custom_personas = app.custom_personas(username=user["username"])
                        creator_personas = app.created_personas(username=user["username"])
                        user_settings = app.load_user_settings(user["username"])
                        public_personas = load_all_public_custom_personas(app.root_workspace)
                        # Exclude the user's own public personas from the public list
                        for key in list(public_personas.keys()):
                            if public_personas[key].get("owner") == user["username"]:
                                public_personas.pop(key, None)
                    self.send_json({
                        "ok": True,
                        "provider": user_settings.get("provider") or app.provider,
                        "default_model": user_settings.get("default_model") or app.default_model,
                        "base_url": user_settings.get("base_url") or app.base_url or default_provider_url(user_settings.get("provider") or app.provider),
                        "image_provider": user_settings.get("image_provider") or app.image_provider,
                        "image_model": user_settings.get("image_model") or app.image_model,
                        "image_edit_model": user_settings.get("image_edit_model") or app.image_edit_model,
                        "image_base_url": user_settings.get("image_base_url") or app.image_base_url,
                        "video_provider": user_settings.get("video_provider") or app.video_provider,
                        "video_model": user_settings.get("video_model") or app.video_model,
                        "video_base_url": user_settings.get("video_base_url") or app.video_base_url,
                        "audio_provider": user_settings.get("audio_provider") or app.audio_provider,
                        "audio_model": user_settings.get("audio_model") or app.audio_model,
                        "audio_base_url": user_settings.get("audio_base_url") or app.audio_base_url,
                        "has_env_key": bool(app.api_key),
                        "personas": {
                            key: safe_persona_metadata(key, value)
                            for key, value in PERSONAS.items()
                        },
                        "custom_personas": with_runtime_metadata(custom_personas),
                        "creator_personas": with_runtime_metadata(creator_personas),
                        "public_personas": with_runtime_metadata(public_personas),
                        "marketplace_personas": with_runtime_metadata(mp_personas),
                        "poq": app.poq,
                    })
                    return
                if path == "/api/models":
                    provider = (self.query_param("provider") or app.provider).strip().lower()
                    api_key, base_url = resolve_model_discovery_credentials(
                        app,
                        provider,
                        api_key_override=self.query_param("apiKey"),
                        base_url_override=self.query_param("baseUrl"),
                    )
                    catalog = list_provider_models(
                        provider=provider,
                        base_url=base_url,
                        api_key=api_key,
                        timeout=min(app.timeout, 20.0),
                    )
                    self.send_json({"ok": True, "provider": provider, "catalog": catalog})
                    return
                if path == "/api/guide/topics":
                    self.send_json({"ok": True, "topics": guide_topics_payload()})
                    return
                if path == "/api/sessions":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    username = user["username"]
                    self.send_json({
                        "ok": True,
                        "active": app.user_active_sessions.get(username, "default"),
                        "sessions": app.list_sessions(username=username),
                    })
                    return
                if path == "/api/self-model":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json({"ok": True, "model": app.self_model()})
                    return
                if path == "/api/trainer/state":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    state = app.trainer.get_state(app.active_session)
                    self.send_json({"ok": True, **state})
                    return
                if path == "/api/memory-model":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json({"ok": True, "model": app.memory_model()})
                    return
                if path == "/api/memories":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json({"ok": True, **app.list_memories()})
                    return
                if path == "/api/history":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json({
                        "ok": True,
                        "history": serialize_history(app.agent.chain),
                        "rings": len(app.agent.chain),
                    })
                    return
                if path == "/api/rings":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    limit = int(self.query_param("limit") or "24")
                    self.send_json({"ok": True, **app.ring_workbench(limit=limit)})
                    return
                if path == "/api/cambium":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json({"ok": True, **app.cambium_workbench()})
                    return
                if path == "/api/overlays":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json(app.list_overlays())
                    return
                if path == "/api/sync-snapshot":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    self.send_json({"ok": True, **app.sync_snapshot()})
                    return
                if path == "/api/verify":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    app.use_session(self.query_param("session"), username=user["username"])
                    ok, status = app.timechain.verify_chain(app.agent.chain)
                    self.send_json({"ok": ok, "status": status, "rings": len(app.agent.chain)})
                    return
                if path == "/api/shared-memory":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    chat.handle_shared_memory_recall(self, app)
                    return
                if path.startswith("/api/session/") and path.endswith("/anchor/list"):
                    self.handle_session_anchor_list(path)
                    return
                if path == "/api/auth/me":
                    auth.handle_auth_me(self)
                    return
                if path == "/api/marketplace":
                    marketplace_routes.handle_catalog(self)
                    return
                if path.startswith("/api/marketplace/"):
                    persona_id = path[len("/api/marketplace/"):].split("/")[0]
                    marketplace_routes.handle_persona_detail(self, persona_id)
                    return
                if path == "/api/subscriptions":
                    marketplace_routes.handle_subscriptions(self)
                    return
                if path == "/api/creator/personas":
                    marketplace_routes.handle_creator_personas(self)
                    return
                if path.startswith("/api/creator/personas/"):
                    rest = path[len("/api/creator/personas/"):]
                    if "/" not in rest:
                        persona_id = rest
                        marketplace_routes.handle_creator_persona_detail(self, persona_id)
                        return
                if path == "/manifest.json":
                    encoded = MANIFEST_JSON.encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                    return
                if path == "/sw.js":
                    encoded = SW_JS.encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                    self.send_header("Content-Length", str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                    return
                if path == "/icon.svg":
                    encoded = ICON_SVG.encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "image/svg+xml")
                    self.send_header("Content-Length", str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                    return
                if path == "/api/imagegen/gallery":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    index = app.load_gallery_index(user["username"])
                    self.send_json({"ok": True, "images": index.get("images", [])})
                    return
                if path == "/api/imagegen/lineage":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    image_id = self.query_param("image_id") or ""
                    if not image_id:
                        self.send_json({"ok": False, "error": "image_id is required"}, HTTPStatus.BAD_REQUEST)
                        return
                    self.send_json(app.image_lineage(user["username"], image_id))
                    return
                if path.startswith("/api/imagegen/image/"):
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    image_id = path[len("/api/imagegen/image/"):]
                    if not image_id or "/" in image_id or ".." in image_id:
                        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                        return
                    img_path = app.gallery_image_path(user["username"], image_id)
                    if not img_path.exists():
                        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                        return
                    data = img_path.read_bytes()
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            except Exception as exc:
                self.send_exception(exc)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            try:
                if path == "/api/chat":
                    self.handle_chat()
                    return
                if path == "/api/sessions":
                    self.handle_create_session()
                    return
                if path == "/api/personas":
                    self.handle_save_persona()
                    return
                if path == "/api/personas/delete":
                    self.handle_delete_persona()
                    return
                if path == "/api/test":
                    self.handle_provider_test()
                    return
                if path == "/api/config":
                    self.handle_save_user_config()
                    return
                if path == "/api/guide/explain":
                    self.handle_guide_explain()
                    return
                if path == "/api/recall":
                    self.handle_recall()
                    return
                if path == "/api/memories":
                    self.handle_memory_action()
                    return
                if path == "/api/reset":
                    self.handle_reset()
                    return
                if path == "/api/freeze":
                    self.handle_freeze()
                    return
                if path == "/api/rewind":
                    self.handle_rewind()
                    return
                if path == "/api/dream":
                    self.handle_dream()
                    return
                if path == "/api/overlays":
                    self.handle_overlay_set()
                    return
                if path == "/api/memory-sync":
                    self.handle_memory_sync()
                    return
                if path == "/api/fleet-import":
                    self.handle_fleet_import()
                    return
                if path == "/api/challenge":
                    self.handle_challenge()
                    return
                if path == "/api/shared-memory/import":
                    self.handle_shared_memory_import()
                    return
                if path == "/api/shared-memory/synthesize":
                    self.handle_shared_memory_synthesize()
                    return
                if path.startswith("/api/session/") and path.endswith("/anchor"):
                    self.handle_session_anchor(path)
                    return
                if path.startswith("/api/session/") and path.endswith("/anchor/auto"):
                    self.handle_session_anchor_auto(path)
                    return
                if path == "/api/sessions/delete":
                    self.handle_delete_session()
                    return
                if path == "/api/sessions/rename":
                    self.handle_rename_session()
                    return
                if path == "/api/auth/register":
                    self.handle_auth_register()
                    return
                if path == "/api/auth/login":
                    self.handle_auth_login()
                    return
                if path == "/api/auth/logout":
                    self.handle_auth_logout()
                    return
                if path.startswith("/api/marketplace/") and path.endswith("/subscribe"):
                    persona_id = path[len("/api/marketplace/"):].rsplit("/", 1)[0]
                    self.handle_subscribe(persona_id)
                    return
                if path.startswith("/api/marketplace/") and path.endswith("/unsubscribe"):
                    persona_id = path[len("/api/marketplace/"):].rsplit("/", 1)[0]
                    self.handle_unsubscribe(persona_id)
                    return
                if path == "/api/creator/personas":
                    self.handle_creator_create()
                    return
                if path.startswith("/api/creator/personas/") and path.endswith("/distill"):
                    persona_id = path[len("/api/creator/personas/"):].rsplit("/", 1)[0]
                    self.handle_creator_distill(persona_id)
                    return
                if path.startswith("/api/creator/personas/") and path.endswith("/publish"):
                    persona_id = path[len("/api/creator/personas/"):].rsplit("/", 1)[0]
                    self.handle_creator_publish(persona_id)
                    return
                if path.startswith("/api/creator/personas/") and path.endswith("/delete"):
                    persona_id = path[len("/api/creator/personas/"):].rsplit("/", 1)[0]
                    self.handle_creator_delete(persona_id)
                    return
                if path == "/api/imagegen/generate":
                    self.handle_imagegen_generate()
                    return
                if path == "/api/imagegen/edit":
                    self.handle_imagegen_edit()
                    return
                if path == "/api/imagegen/redefine":
                    self.handle_imagegen_redefine()
                    return
                if path == "/api/imagegen/delete":
                    self.handle_imagegen_delete()
                    return

                if path == "/api/videogen/gallery":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    index = app.load_videogen_index(user["username"])
                    self.send_json({"ok": True, "videos": index.get("videos", [])})
                    return

                if path == "/api/videogen/lineage":
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                        return
                    video_id = self.query_param("video_id")
                    data = app.video_lineage(user["username"], video_id or "")
                    self.send_json(data)
                    return

                if path.startswith("/api/videogen/video/"):
                    try:
                        user = self._auth_user()
                    except PermissionError as exc:
                        self.send_error(HTTPStatus.UNAUTHORIZED)
                        return
                    video_id = path[len("/api/videogen/video/"):]
                    if not video_id or "/" in video_id or ".." in video_id:
                        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                        return
                    vid_path = app.videogen_video_path(user["username"], video_id)
                    if not vid_path.exists():
                        self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                        return
                    # Serve with proper video mime and caching
                    data = vid_path.read_bytes()
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("Cache-Control", "public, max-age=31536000, immutable")
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    self.wfile.write(data)
                    return

                if path == "/api/videogen/generate":
                    self.handle_videogen_generate()
                    return
                if path == "/api/videogen/img2vid":
                    self.handle_videogen_img2vid()
                    return
                if path == "/api/videogen/remix":
                    self.handle_videogen_remix()
                    return
                if path == "/api/videogen/delete":
                    self.handle_videogen_delete()
                    return
                if path == "/api/audiogen/generate":
                    self.handle_audiogen_generate()
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            except Exception as exc:
                self.send_exception(exc)

        def handle_imagegen_generate(self) -> None:
            imagegen.handle_imagegen_generate(self, app)

        def handle_imagegen_edit(self) -> None:
            imagegen.handle_imagegen_edit(self, app)

        def handle_imagegen_redefine(self) -> None:
            imagegen.handle_imagegen_redefine(self, app)

        def handle_imagegen_delete(self) -> None:
            imagegen.handle_imagegen_delete(self, app)

        def handle_videogen_generate(self) -> None:
            videogen.handle_videogen_generate(self, app)

        def handle_videogen_img2vid(self) -> None:
            videogen.handle_videogen_img2vid(self, app)

        def handle_videogen_remix(self) -> None:
            videogen.handle_videogen_remix(self, app)

        def handle_videogen_delete(self) -> None:
            videogen.handle_videogen_delete(self, app)

        def handle_audiogen_generate(self) -> None:
            audiogen.handle_audiogen_generate(self, app)

        def handle_chat(self) -> None:
            chat.handle_chat(self, app)

        def handle_recall(self) -> None:
            chat.handle_recall(self, app)

        def handle_memory_action(self) -> None:
            chat.handle_memory_action(self, app)

        def handle_reset(self) -> None:
            chat.handle_reset(self, app)

        def handle_freeze(self) -> None:
            chat.handle_freeze(self, app)

        def handle_rewind(self) -> None:
            chat.handle_rewind(self, app)

        def handle_dream(self) -> None:
            chat.handle_dream(self, app)

        def handle_overlay_set(self) -> None:
            chat.handle_overlay_set(self, app)

        def handle_memory_sync(self) -> None:
            chat.handle_memory_sync(self, app)

        def handle_fleet_import(self) -> None:
            chat.handle_fleet_import(self, app)

        def handle_challenge(self) -> None:
            chat.handle_challenge(self, app)

        def handle_shared_memory_import(self) -> None:
            chat.handle_shared_memory_import(self, app)

        def handle_shared_memory_synthesize(self) -> None:
            chat.handle_shared_memory_synthesize(self, app)

        def handle_create_session(self) -> None:
            chat.handle_create_session(self, app)

        def handle_delete_session(self) -> None:
            chat.handle_delete_session(self, app)

        def handle_rename_session(self) -> None:
            chat.handle_rename_session(self, app)

        def handle_provider_test(self) -> None:
            chat.handle_provider_test(self, app)

        def handle_save_user_config(self) -> None:
            chat.handle_save_user_config(self, app)

        def handle_guide_explain(self) -> None:
            chat.handle_guide_explain(self, app)

        def handle_save_persona(self) -> None:
            chat.handle_save_persona(self, app)

        def handle_delete_persona(self) -> None:
            chat.handle_delete_persona(self, app)

        def handle_auth_register(self) -> None:
            auth.handle_auth_register(self)

        def handle_auth_login(self) -> None:
            auth.handle_auth_login(self)

        def handle_auth_logout(self) -> None:
            auth.handle_auth_logout(self)

        def handle_subscribe(self, persona_id: str) -> None:
            marketplace_routes.handle_subscribe(self, persona_id)

        def handle_unsubscribe(self, persona_id: str) -> None:
            marketplace_routes.handle_unsubscribe(self, persona_id)

        def handle_creator_create(self) -> None:
            marketplace_routes.handle_creator_create(self)

        def handle_creator_distill(self, persona_id: str) -> None:
            marketplace_routes.handle_creator_distill(self, app, persona_id)

        def handle_creator_publish(self, persona_id: str) -> None:
            marketplace_routes.handle_creator_publish(self, persona_id)

        def handle_creator_delete(self, persona_id: str) -> None:
            marketplace_routes.handle_creator_delete(self, persona_id)

        def _session_id_from_anchor_path(self, path: str, suffix: str) -> str:
            prefix = "/api/session/"
            if not path.startswith(prefix) or not path.endswith(suffix):
                return ""
            session_id = path[len(prefix): -len(suffix)]
            return sanitize_session_id(urllib.parse.unquote(session_id.strip("/")))

        def handle_session_anchor_list(self, path: str) -> None:
            try:
                user = self._auth_user()
            except PermissionError as exc:
                self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                return
            session_id = self._session_id_from_anchor_path(path, "/anchor/list")
            app.use_session(session_id, username=user["username"])
            self.send_json(app.list_memory_anchors())

        def handle_session_anchor(self, path: str) -> None:
            try:
                user = self._auth_user()
            except PermissionError as exc:
                self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                return
            session_id = self._session_id_from_anchor_path(path, "/anchor")
            app.use_session(session_id, username=user["username"])
            try:
                self.send_json(app.write_memory_anchor())
            except PermissionError as exc:
                self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.CONFLICT)

        def handle_session_anchor_auto(self, path: str) -> None:
            try:
                user = self._auth_user()
            except PermissionError as exc:
                self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.UNAUTHORIZED)
                return
            payload = self.read_json()
            session_id = self._session_id_from_anchor_path(path, "/anchor/auto")
            app.use_session(session_id, username=user["username"])
            try:
                interval = int(payload.get("interval", 100) or 100)
            except (TypeError, ValueError):
                self.send_json({"ok": False, "error": "interval must be an integer"}, HTTPStatus.BAD_REQUEST)
                return
            result = app.configure_auto_memory_anchor(
                enabled=bool(payload.get("enabled", True)),
                interval=interval,
            )
            self.send_json(result)

        def query_param(self, name: str) -> str:
            parsed = urlparse(self.path)
            pairs = [part.split("=", 1) for part in parsed.query.split("&") if part]
            for key, value in pairs:
                if key == name:
                    return urllib.parse.unquote_plus(value)
            return ""

        def read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)

        def send_html(self, html: str) -> None:
            encoded = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def send_json(self, body: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                # Client closed the connection (e.g. browser timed out or refreshed)
                # before the response could be delivered.  The request was already
                # processed and persisted, so this is not a real error.
                pass

        def send_exception(self, exc: Exception) -> None:
            traceback.print_exc()
            self.send_json(
                {"ok": False, "error": str(exc), "type": type(exc).__name__},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return Handler

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the standalone CypherTempre chat PoC.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--workspace",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent.parent,
        help="Directory where .timechain will be created.",
    )
    parser.add_argument(
        "--timechain-path",
        type=pathlib.Path,
        default=DEFAULT_TIMECHAIN_PATH,
        help="Path to the timechain.py skill script.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Default model. Defaults to Morpheus gemma-4-uncensored.",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM provider (morpheus, openrouter, kimi-code, kimi, or other). Defaults to morpheus.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key. If omitted, the UI can send a browser-session key.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible endpoint or /v1 base URL. Defaults from provider.",
    )
    parser.add_argument(
        "--openrouter-api-key",
        default=None,
        help="Deprecated. Use --api-key instead.",
    )
    parser.add_argument(
        "--env-file",
        type=pathlib.Path,
        default=DEFAULT_ENV_PATH,
        help="Local env file for persistent test keys.",
    )
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--openrouter-timeout", type=float, default=None, help="Deprecated. Use --timeout instead.")
    parser.add_argument(
        "--poq-enabled",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable the post-generation PoQ gate.",
    )
    parser.add_argument("--poq-min-score", type=float, default=None, help="Minimum PoQ score required for release.")
    parser.add_argument("--poq-max-retries", type=int, default=None, help="Maximum PoQ repair attempts.")
    parser.add_argument(
        "--poq-overfitting-check",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable deterministic PoQ overfitting detection.",
    )
    return parser

def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}

def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default

def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default

def build_poq_config(args: argparse.Namespace) -> dict[str, Any]:
    enabled = _env_bool("POQ_ENABLED", DEFAULT_POQ_ENABLED)
    min_score = _env_float("POQ_MIN_SCORE", float(DEFAULT_POQ_MIN_SCORE))
    max_retries = _env_int("POQ_MAX_RETRIES", int(DEFAULT_POQ_MAX_RETRIES))
    overfitting_check = _env_bool("POQ_OVERFITTING_CHECK", DEFAULT_POQ_OVERFITTING_CHECK)
    if args.poq_enabled is not None:
        enabled = bool(args.poq_enabled)
    if args.poq_min_score is not None:
        min_score = float(args.poq_min_score)
    if args.poq_max_retries is not None:
        max_retries = int(args.poq_max_retries)
    if args.poq_overfitting_check is not None:
        overfitting_check = bool(args.poq_overfitting_check)
    return {
        "enabled": enabled,
        "min_score": min_score,
        "max_retries": max(0, max_retries),
        "overfitting_check": overfitting_check,
    }

def migrate_global_data_to_users(app: App) -> None:
    users_path = app.root_workspace / "data" / "users.json"
    if not users_path.exists():
        return
    try:
        users = json.loads(users_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    if not users or len(users) != 1:
        return
    username = next(iter(users.keys()))
    if app.sessions_root.exists():
        user_sessions = app.user_sessions_root(username)
        user_sessions.mkdir(parents=True, exist_ok=True)
        for path in list(app.sessions_root.iterdir()):
            if path.is_dir():
                dest = user_sessions / path.name
                if not dest.exists():
                    shutil.move(str(path), str(dest))
                    print(f"Migrated session '{path.name}' to user '{username}'")
    global_personas = custom_personas_path(app.root_workspace)
    if global_personas.exists():
        user_personas = app.user_custom_personas_path(username)
        user_personas.parent.mkdir(parents=True, exist_ok=True)
        if not user_personas.exists():
            shutil.copy2(str(global_personas), str(user_personas))
            print(f"Migrated custom personas to user '{username}'")

def main() -> int:
    args = build_parser().parse_args()
    load_local_env(args.env_file)
    provider = (args.provider or os.environ.get("PROVIDER", DEFAULT_PROVIDER)).strip().lower()
    if provider == "morpheus":
        default_model = args.model or env_value("MODEL", "MORPHEUS_MODEL") or DEFAULT_MODEL
        api_key = args.api_key or env_value("API_KEY", "MORPHEUS_API_KEY")
        base_url = args.base_url or env_value("BASE_URL", "MORPHEUS_BASE_URL")
    elif provider == "kimi-code":
        provider_default_model = "kimi-for-coding"
        default_model = args.model or env_value("MODEL", "KIMI_MODEL_NAME") or provider_default_model
        api_key = args.api_key or env_value("API_KEY", "KIMI_API_KEY")
        base_url = args.base_url or env_value("BASE_URL", "KIMI_BASE_URL")
    elif provider == "kimi":
        default_model = args.model or env_value("MODEL", "KIMI_MODEL_NAME") or "kimi-k2.6"
        api_key = args.api_key or env_value("API_KEY", "KIMI_API_KEY")
        base_url = args.base_url or env_value("BASE_URL", "KIMI_BASE_URL")
    else:
        default_model = args.model or os.environ.get("MODEL") or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
        api_key = args.api_key or os.environ.get("API_KEY") or args.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        base_url = args.base_url or os.environ.get("BASE_URL", "")
    timeout = args.timeout if args.timeout is not None else (args.openrouter_timeout or 45.0)
    app = App(
        args.workspace,
        args.timechain_path,
        default_model=default_model,
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        poq=build_poq_config(args),
        image_provider=os.environ.get("IMAGE_PROVIDER", provider).strip().lower(),
        image_model=os.environ.get("IMAGE_MODEL", "").strip(),
        image_edit_model=os.environ.get("IMAGE_EDIT_MODEL", "").strip(),
        image_api_key=os.environ.get("IMAGE_API_KEY", "").strip() or api_key,
        image_base_url=os.environ.get("IMAGE_BASE_URL", "").strip() or base_url,
        video_provider=os.environ.get("VIDEO_PROVIDER", provider).strip().lower(),
        video_model=os.environ.get("VIDEO_MODEL", "").strip(),
        video_api_key=os.environ.get("VIDEO_API_KEY", "").strip() or api_key,
        video_base_url=os.environ.get("VIDEO_BASE_URL", "").strip() or base_url,
        audio_provider=os.environ.get("AUDIO_PROVIDER", provider).strip().lower(),
        audio_model=os.environ.get("AUDIO_MODEL", "").strip(),
        audio_api_key=os.environ.get("AUDIO_API_KEY", "").strip() or api_key,
        audio_base_url=os.environ.get("AUDIO_BASE_URL", "").strip() or base_url,
    )
    migrate_global_data_to_users(app)
    handler = make_handler(app)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    url = f"http://{args.host}:{args.port}"
    print(f"CypherTempre chat PoC running at {url}")
    print(f"Workspace: {app.workspace}")
    print(f"Default model: {app.default_model}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
