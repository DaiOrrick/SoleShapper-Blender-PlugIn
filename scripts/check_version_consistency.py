#!/usr/bin/env python3
"""Validate extension metadata and version consistency."""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "blender_manifest.toml"
ADDON_CORE_PATH = REPO_ROOT / "addon_core.py"
MAX_SHORT_TEXT_LEN = 64


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _manifest_value(manifest_text: str, key: str) -> str:
    pattern = re.compile(rf'(?m)^{re.escape(key)}\s*=\s*"([^"]+)"')
    match = pattern.search(manifest_text)
    if not match:
        raise ValueError(f"Missing required manifest key: {key}")
    return match.group(1).strip()


def _bl_info_version(path: Path) -> tuple[int, int, int]:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "bl_info":
                bl_info = ast.literal_eval(node.value)
                version = bl_info.get("version")
                if (
                    isinstance(version, tuple)
                    and len(version) == 3
                    and all(isinstance(item, int) for item in version)
                ):
                    return version
                raise ValueError("bl_info['version'] must be an int tuple of length 3")
    raise ValueError("Could not find top-level bl_info assignment")


def _parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError("Manifest version must be semantic version format: X.Y.Z")
    return tuple(int(part) for part in parts)


def main() -> int:
    if not MANIFEST_PATH.is_file():
        return _error(f"Manifest not found: {MANIFEST_PATH}")
    if not ADDON_CORE_PATH.is_file():
        return _error(f"Add-on core not found: {ADDON_CORE_PATH}")

    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")

    try:
        addon_id = _manifest_value(manifest_text, "id")
        manifest_version_text = _manifest_value(manifest_text, "version")
        tagline = _manifest_value(manifest_text, "tagline")
        files_reason = _manifest_value(manifest_text, "files")
    except ValueError as exc:
        return _error(str(exc))

    if len(tagline) > MAX_SHORT_TEXT_LEN:
        return _error(
            f"Manifest 'tagline' is {len(tagline)} chars (max {MAX_SHORT_TEXT_LEN})."
        )
    if len(files_reason) > MAX_SHORT_TEXT_LEN:
        return _error(
            f"Manifest permission reason 'files' is {len(files_reason)} chars "
            f"(max {MAX_SHORT_TEXT_LEN})."
        )

    try:
        manifest_version = _parse_semver(manifest_version_text)
        bl_info_version = _bl_info_version(ADDON_CORE_PATH)
    except ValueError as exc:
        return _error(str(exc))

    if manifest_version != bl_info_version:
        return _error(
            "Version mismatch: blender_manifest.toml="
            f"{manifest_version_text} but bl_info={'.'.join(map(str, bl_info_version))}"
        )

    git_tag = os.getenv("GITHUB_REF_NAME", "").strip()
    if git_tag.startswith("v"):
        tag_version = git_tag[1:]
        if tag_version != manifest_version_text:
            return _error(
                f"Tag version mismatch: tag={git_tag} but manifest={manifest_version_text}"
            )

    print(
        "Metadata check passed "
        f"(id={addon_id}, version={manifest_version_text}, bl_info={bl_info_version})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
