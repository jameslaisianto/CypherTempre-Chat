#!/usr/bin/env python3
"""CypherTempre Marketplace — file-based auth, persona catalog, and creator tools.

Pure Python stdlib. No SQL, no external payment processing.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import pathlib
import re
import secrets
import shutil
import uuid
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = pathlib.Path(__file__).resolve().parent / "data"
USERS_PATH = DATA_DIR / "users.json"
AUTH_SESSIONS_PATH = DATA_DIR / "auth_sessions.json"
MARKETPLACE_DIR = DATA_DIR / "marketplace"
CATALOG_PATH = MARKETPLACE_DIR / "catalog.json"
USERS_DIR = DATA_DIR / "users"

# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------

ENV_PATH = pathlib.Path(__file__).resolve().parent / ".env.local"


def _ensure_auth_secret() -> str:
    """Load or generate a persistent HMAC secret."""
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("AUTH_SECRET="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    secret = secrets.token_urlsafe(32)
    with ENV_PATH.open("a", encoding="utf-8") as f:
        f.write(f"\nAUTH_SECRET={secret}\n")
    return secret


AUTH_SECRET = _ensure_auth_secret()

# ---------------------------------------------------------------------------
# Password hashing (stdlib only)
# ---------------------------------------------------------------------------

_SALT_LEN = 32
_ITERATIONS = 260_000


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(_SALT_LEN)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${base64.b64encode(hashed).decode('ascii')}"


def _verify_password(password: str, hashed: str) -> bool:
    try:
        _, iterations, salt, encoded = hashed.split("$")
        iterations = int(iterations)
        expected = base64.b64decode(encoded.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), iterations)
        return hmac.compare_digest(expected, actual)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _load_json(path: pathlib.Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _sanitize_username(value: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower())[:40].strip("-")


def create_user(username: str, display_name: str, password: str, role: str = "subscriber") -> dict[str, Any]:
    username = _sanitize_username(username)
    if not username or len(username) < 2:
        raise ValueError("Username must be at least 2 chars (alphanumeric, -, _).")
    if not password or len(password) < 4:
        raise ValueError("Password must be at least 4 chars.")
    users = _load_json(USERS_PATH, {})
    if username in users:
        raise ValueError(f"User '{username}' already exists.")
    users[username] = {
        "username": username,
        "display_name": display_name.strip()[:60] or username,
        "password_hash": _hash_password(password),
        "role": role if role in {"subscriber", "creator", "admin"} else "subscriber",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "stats": {"personas_created": 0, "total_subscribers": 0},
    }
    _save_json(USERS_PATH, users)
    return {"username": username, "display_name": users[username]["display_name"], "role": users[username]["role"]}


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    username = _sanitize_username(username)
    users = _load_json(USERS_PATH, {})
    user = users.get(username)
    if not user:
        return None
    if not _verify_password(password, user.get("password_hash", "")):
        return None
    return {
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
        "created_at": user.get("created_at", ""),
        "stats": user.get("stats", {}),
    }


def get_user(username: str) -> dict[str, Any] | None:
    username = _sanitize_username(username)
    users = _load_json(USERS_PATH, {})
    user = users.get(username)
    if not user:
        return None
    return {
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
        "created_at": user.get("created_at", ""),
        "stats": user.get("stats", {}),
    }


def list_users() -> list[dict[str, Any]]:
    users = _load_json(USERS_PATH, {})
    return [
        {
            "username": u["username"],
            "display_name": u["display_name"],
            "role": u["role"],
            "created_at": u.get("created_at", ""),
            "stats": u.get("stats", {}),
        }
        for u in users.values()
    ]


def set_user_role(username: str, role: str) -> dict[str, Any]:
    username = _sanitize_username(username)
    users = _load_json(USERS_PATH, {})
    if username not in users:
        raise KeyError(f"Unknown user: {username}")
    users[username]["role"] = role if role in {"subscriber", "creator", "admin"} else "subscriber"
    _save_json(USERS_PATH, users)
    return get_user(username)


# ---------------------------------------------------------------------------
# Sessions (auth tokens)
# ---------------------------------------------------------------------------

TOKEN_TTL_HOURS = 168  # 7 days


def _sign_token(token_id: str, username: str, expires: str) -> str:
    payload = f"{token_id}:{username}:{expires}"
    sig = hmac.new(AUTH_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()[:32]
    return base64.urlsafe_b64encode(f"{payload}:{sig}".encode("utf-8")).decode("ascii").rstrip("=")


def _verify_token(token: str) -> dict[str, Any] | None:
    try:
        padded = token + "=" * (-len(token) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        payload_part, sig = decoded.rsplit(":", 1)
        token_id, username, expires = payload_part.split(":", 2)
        expected = hmac.new(AUTH_SECRET.encode("utf-8"), f"{token_id}:{username}:{expires}".encode("utf-8"), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(expected, sig):
            return None
        exp = dt.datetime.fromisoformat(expires)
        if dt.datetime.now(dt.timezone.utc) > exp:
            return None
        return {"token_id": token_id, "username": username, "expires": expires}
    except Exception:
        return None


def create_auth_session(username: str) -> str:
    username = _sanitize_username(username)
    token_id = secrets.token_urlsafe(16)
    expires = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=TOKEN_TTL_HOURS)).isoformat()
    token = _sign_token(token_id, username, expires)
    sessions = _load_json(AUTH_SESSIONS_PATH, {})
    sessions[token_id] = {"username": username, "expires": expires, "created_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    _save_json(AUTH_SESSIONS_PATH, sessions)
    return token


def delete_auth_session(token: str) -> None:
    verified = _verify_token(token)
    if verified:
        sessions = _load_json(AUTH_SESSIONS_PATH, {})
        sessions.pop(verified["token_id"], None)
        _save_json(AUTH_SESSIONS_PATH, sessions)


def get_auth_user(token: str) -> dict[str, Any] | None:
    verified = _verify_token(token)
    if not verified:
        return None
    sessions = _load_json(AUTH_SESSIONS_PATH, {})
    sess = sessions.get(verified["token_id"])
    if not sess:
        return None
    exp = dt.datetime.fromisoformat(sess["expires"])
    if dt.datetime.now(dt.timezone.utc) > exp:
        return None
    return get_user(verified["username"])


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

def _subscriptions_path(username: str) -> pathlib.Path:
    return USERS_DIR / _sanitize_username(username) / "subscriptions.json"


def get_subscriptions(username: str) -> list[dict[str, Any]]:
    return _load_json(_subscriptions_path(username), [])


def is_subscribed(username: str, persona_id: str) -> bool:
    subs = get_subscriptions(username)
    return any(s.get("persona_id") == persona_id for s in subs)


def subscribe(username: str, persona_id: str) -> dict[str, Any]:
    subs = get_subscriptions(username)
    if any(s.get("persona_id") == persona_id for s in subs):
        raise ValueError("Already subscribed.")
    subs.append({
        "persona_id": persona_id,
        "subscribed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "expires_at": None,
        "access_level": "full",
    })
    _save_json(_subscriptions_path(username), subs)
    # Update catalog stats
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    entry = catalog.get("personas", {}).get(persona_id)
    if entry:
        entry.setdefault("stats", {})
        entry["stats"]["subscribers"] = entry["stats"].get("subscribers", 0) + 1
        _save_json(CATALOG_PATH, catalog)
    return {"subscribed": True, "persona_id": persona_id}


def unsubscribe(username: str, persona_id: str) -> dict[str, Any]:
    subs = get_subscriptions(username)
    subs = [s for s in subs if s.get("persona_id") != persona_id]
    _save_json(_subscriptions_path(username), subs)
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    entry = catalog.get("personas", {}).get(persona_id)
    if entry:
        entry.setdefault("stats", {})
        entry["stats"]["subscribers"] = max(0, entry["stats"].get("subscribers", 0) - 1)
        _save_json(CATALOG_PATH, catalog)
    return {"unsubscribed": True, "persona_id": persona_id}


# ---------------------------------------------------------------------------
# Creator workspaces
# ---------------------------------------------------------------------------

def _creator_dir(username: str) -> pathlib.Path:
    return USERS_DIR / _sanitize_username(username) / "created"


def list_created_personas(username: str) -> list[dict[str, Any]]:
    creator_dir = _creator_dir(username)
    if not creator_dir.exists():
        return []
    results = []
    for path in sorted(creator_dir.iterdir()):
        if not path.is_dir():
            continue
        manifest = _load_json(path / "manifest.json", {})
        chain_path = path / ".timechain" / "chain.jsonl"
        rings = 0
        if chain_path.exists():
            with chain_path.open("r", encoding="utf-8") as f:
                rings = sum(1 for _ in f)
        results.append({
            "persona_id": path.name,
            "name": manifest.get("name", "Untitled"),
            "domain": manifest.get("domain", "auto"),
            "tagline": manifest.get("tagline", ""),
            "status": manifest.get("status", "draft"),
            "rings": rings,
            "created_at": manifest.get("created_at", ""),
            "published_at": manifest.get("published_at", ""),
        })
    return results


def get_created_persona(username: str, persona_id: str) -> dict[str, Any] | None:
    path = _creator_dir(username) / persona_id
    if not path.exists():
        return None
    manifest = _load_json(path / "manifest.json", {})
    system = ""
    system_path = path / "system.txt"
    if system_path.exists():
        system = system_path.read_text(encoding="utf-8")
    return {
        "persona_id": persona_id,
        "name": manifest.get("name", "Untitled"),
        "domain": manifest.get("domain", "auto"),
        "tagline": manifest.get("tagline", ""),
        "system": system,
        "status": manifest.get("status", "draft"),
        "created_at": manifest.get("created_at", ""),
        "published_at": manifest.get("published_at", ""),
    }


def save_created_persona(username: str, persona_id: str | None, data: dict[str, Any]) -> dict[str, Any]:
    pid = persona_id or f"mp_{uuid.uuid4().hex[:12]}"
    path = _creator_dir(username) / pid
    path.mkdir(parents=True, exist_ok=True)
    manifest = _load_json(path / "manifest.json", {})
    manifest.update({
        "persona_id": pid,
        "owner": _sanitize_username(username),
        "name": str(data.get("name", manifest.get("name", "Untitled"))).strip()[:80],
        "domain": str(data.get("domain", manifest.get("domain", "auto"))).strip()[:40],
        "tagline": str(data.get("tagline", manifest.get("tagline", ""))).strip()[:200],
        "status": manifest.get("status", "draft"),
        "created_at": manifest.get("created_at", dt.datetime.now(dt.timezone.utc).isoformat()),
    })
    if "system" in data:
        (path / "system.txt").write_text(str(data["system"]).strip()[:8000], encoding="utf-8")
    _save_json(path / "manifest.json", manifest)
    return {**manifest, "persona_id": pid}


def delete_created_persona(username: str, persona_id: str) -> None:
    path = _creator_dir(username) / persona_id
    if path.exists():
        shutil.rmtree(path)


def get_creator_workspace(username: str, persona_id: str) -> pathlib.Path:
    path = _creator_dir(username) / persona_id
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Distill & Publish
# ---------------------------------------------------------------------------

def distill_persona(username: str, persona_id: str, timechain_module: Any, min_brightness: float = 0.6) -> dict[str, Any]:
    creator_dir = _creator_dir(username) / persona_id
    if not creator_dir.exists():
        raise KeyError(f"Persona not found: {persona_id}")

    # Load chain
    chain_path = creator_dir / ".timechain" / "chain.jsonl"
    rings: list[dict[str, Any]] = []
    if chain_path.exists():
        with chain_path.open("r", encoding="utf-8") as f:
            rings = [json.loads(line) for line in f if line.strip()]

    # Filter bright rings
    bright = [r for r in rings if r.get("brightness", 0) >= min_brightness and r.get("kind") == "interaction"]
    bright.sort(key=lambda r: r.get("brightness", 0), reverse=True)
    top = bright[:20]

    total_mass = sum(r.get("brightness", 0) for r in rings)
    domains: dict[str, float] = {}
    for r in rings:
        d = r.get("domain", "unknown")
        domains[d] = domains.get(d, 0) + r.get("brightness", 0)
    top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]

    capsule = {
        "persona_id": persona_id,
        "distilled_from": len(rings),
        "rings": [
            {
                "n": r.get("n"),
                "domain": r.get("domain"),
                "content": str(r.get("content", ""))[:600],
                "brightness": r.get("brightness"),
                "tags": r.get("tags", []),
                "epistemic": r.get("epistemic", "known"),
            }
            for r in top
        ],
        "summary": f"Distilled from {len(rings)} rings. Top domains: {', '.join(d for d, _ in top_domains)}.",
        "temporal_mass": round(total_mass, 3),
        "top_domains": [d for d, _ in top_domains],
    }
    _save_json(creator_dir / "capsule.json", capsule)
    return capsule


def publish_persona(username: str, persona_id: str, price_data: dict[str, Any] | None = None) -> dict[str, Any]:
    creator_dir = _creator_dir(username) / persona_id
    if not creator_dir.exists():
        raise KeyError(f"Persona not found: {persona_id}")

    manifest = _load_json(creator_dir / "manifest.json", {})
    manifest["status"] = "pending"
    manifest["published_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    if price_data:
        manifest["price"] = {
            "model": str(price_data.get("model", "free")),
            "amount": float(price_data.get("amount", 0)),
            "currency": str(price_data.get("currency", "USD")),
        }
    else:
        manifest.setdefault("price", {"model": "free", "amount": 0, "currency": "USD"})
    manifest.setdefault("stats", {"subscribers": 0, "rating": 0, "temporal_mass": 0})
    _save_json(creator_dir / "manifest.json", manifest)

    # Copy to marketplace
    mp_dir = MARKETPLACE_DIR / "personas" / persona_id
    mp_dir.mkdir(parents=True, exist_ok=True)
    for fname in ["manifest.json", "system.txt", "config.json", "capsule.json"]:
        src = creator_dir / fname
        if src.exists():
            shutil.copy2(src, mp_dir / fname)

    # Update catalog
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    catalog.setdefault("personas", {})
    catalog["personas"][persona_id] = {
        "persona_id": persona_id,
        "owner": manifest.get("owner", username),
        "name": manifest.get("name", "Untitled"),
        "tagline": manifest.get("tagline", ""),
        "domain": manifest.get("domain", "auto"),
        "status": manifest["status"],
        "price": manifest.get("price", {"model": "free", "amount": 0, "currency": "USD"}),
        "stats": manifest.get("stats", {"subscribers": 0, "rating": 0, "temporal_mass": 0}),
        "created_at": manifest.get("created_at", ""),
        "published_at": manifest["published_at"],
    }
    _save_json(CATALOG_PATH, catalog)
    return catalog["personas"][persona_id]


def unpublish_persona(username: str, persona_id: str) -> None:
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    entry = catalog.get("personas", {}).get(persona_id)
    if entry and entry.get("owner") == username:
        entry["status"] = "archived"
        _save_json(CATALOG_PATH, catalog)
    creator_dir = _creator_dir(username) / persona_id
    if creator_dir.exists():
        manifest = _load_json(creator_dir / "manifest.json", {})
        manifest["status"] = "archived"
        _save_json(creator_dir / "manifest.json", manifest)


# ---------------------------------------------------------------------------
# Marketplace catalog
# ---------------------------------------------------------------------------

def get_catalog() -> list[dict[str, Any]]:
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    return list(catalog.get("personas", {}).values())


def get_marketplace_persona(persona_id: str) -> dict[str, Any] | None:
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    entry = catalog.get("personas", {}).get(persona_id)
    if not entry:
        return None
    # Load capsule
    capsule = _load_json(MARKETPLACE_DIR / "personas" / persona_id / "capsule.json", {})
    system = ""
    system_path = MARKETPLACE_DIR / "personas" / persona_id / "system.txt"
    if system_path.exists():
        system = system_path.read_text(encoding="utf-8")
    return {
        **entry,
        "system": system,
        "capsule": capsule,
    }


def approve_persona(persona_id: str) -> dict[str, Any] | None:
    catalog = _load_json(CATALOG_PATH, {"personas": {}})
    entry = catalog.get("personas", {}).get(persona_id)
    if not entry:
        return None
    entry["status"] = "published"
    _save_json(CATALOG_PATH, catalog)
    return entry


# ---------------------------------------------------------------------------
# Middleware helpers
# ---------------------------------------------------------------------------

def get_cookie_token(headers: dict[str, str]) -> str:
    cookie = headers.get("Cookie", "")
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("ct_auth="):
            return part.split("=", 1)[1].strip()
    return ""


def require_auth(headers: dict[str, str]) -> dict[str, Any]:
    token = get_cookie_token(headers)
    user = get_auth_user(token)
    if not user:
        raise PermissionError("Authentication required.")
    return user


def require_role(headers: dict[str, str], role: str) -> dict[str, Any]:
    user = require_auth(headers)
    roles = {"subscriber": 0, "creator": 1, "admin": 2}
    if roles.get(user["role"], -1) < roles.get(role, 999):
        raise PermissionError(f"Role '{role}' required.")
    return user
