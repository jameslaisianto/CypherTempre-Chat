"""User data export / backup / restore packs for CypherTempre."""

from __future__ import annotations

import datetime as dt
import io
import json
import pathlib
import shutil
import zipfile
from typing import Any, Iterable


PACK_VERSION = 1
USER_PACK_ROOTS = (
    "sessions",
    "identity",
    "gallery",
    "videogen",
    "created",
)
USER_PACK_FILES = (
    "settings.json",
    "custom_personas.json",
    "subscriptions.json",
)


def _user_root(workspace: pathlib.Path, username: str) -> pathlib.Path:
    return (workspace / "data" / "users" / username).resolve()


def _safe_under(root: pathlib.Path, path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_export_manifest(username: str, *, note: str = "") -> dict[str, Any]:
    return {
        "pack_version": PACK_VERSION,
        "app": "CypherTempre/1.0",
        "username": username,
        "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "note": note,
        "includes": {
            "roots": list(USER_PACK_ROOTS),
            "files": list(USER_PACK_FILES),
        },
    }


def export_user_pack(
    workspace: pathlib.Path,
    username: str,
    *,
    note: str = "",
    include_gallery_binaries: bool = True,
) -> bytes:
    """Return a zip archive of the user's local CypherTempre state."""
    user_root = _user_root(workspace, username)
    if not user_root.exists():
        raise FileNotFoundError(f"No user data for {username}")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        manifest = build_export_manifest(username, note=note)
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        for name in USER_PACK_FILES:
            path = user_root / name
            if path.is_file():
                zf.write(path, arcname=f"user/{name}")

        for root_name in USER_PACK_ROOTS:
            root = user_root / root_name
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                rel = path.relative_to(user_root).as_posix()
                if not include_gallery_binaries and root_name in {"gallery", "videogen"}:
                    # Keep indexes and timechains; skip large media blobs.
                    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".wav", ".mp3"}:
                        continue
                zf.write(path, arcname=f"user/{rel}")

    return buffer.getvalue()


def inspect_pack(data: bytes) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
        names = zf.namelist()
        manifest: dict[str, Any] = {}
        if "manifest.json" in names:
            try:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            except Exception:
                manifest = {}
        return {
            "ok": True,
            "files": len(names),
            "manifest": manifest,
            "has_user_tree": any(n.startswith("user/") for n in names),
        }


def restore_user_pack(
    workspace: pathlib.Path,
    username: str,
    data: bytes,
    *,
    mode: str = "merge",
) -> dict[str, Any]:
    """Restore a pack into the user's data directory.

    mode:
      - merge: overwrite files present in the pack, leave others alone
      - replace: move existing user dir aside, then extract pack user tree
    """
    user_root = _user_root(workspace, username)
    user_root.parent.mkdir(parents=True, exist_ok=True)
    info = inspect_pack(data)
    if not info.get("has_user_tree"):
        raise ValueError("Invalid pack: missing user/ tree")

    archived = None
    if mode == "replace" and user_root.exists():
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archived = user_root.with_name(f"{user_root.name}.pre-restore-{stamp}")
        shutil.move(str(user_root), str(archived))
        user_root.mkdir(parents=True, exist_ok=True)
    else:
        user_root.mkdir(parents=True, exist_ok=True)

    restored = 0
    with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
        for name in zf.namelist():
            if not name.startswith("user/") or name.endswith("/"):
                continue
            rel = name[len("user/") :]
            if not rel or ".." in pathlib.PurePosixPath(rel).parts:
                continue
            dest = (user_root / rel).resolve()
            if not _safe_under(user_root, dest):
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, dest.open("wb") as out:
                shutil.copyfileobj(src, out)
            restored += 1

    return {
        "ok": True,
        "username": username,
        "mode": mode,
        "restored_files": restored,
        "archived_previous": str(archived) if archived else None,
        "manifest": info.get("manifest") or {},
    }
