#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SMOKE_SCRIPT="$REPO_ROOT/scripts/runtime_smoke.py"

if [[ ! -f "$SMOKE_SCRIPT" ]]; then
  echo "Smoke test script not found: $SMOKE_SCRIPT" >&2
  exit 1
fi

BLENDER_BIN_VALUE="${BLENDER_BIN:-}"

if [[ -z "$BLENDER_BIN_VALUE" ]]; then
  if command -v blender >/dev/null 2>&1; then
    BLENDER_BIN_VALUE="$(command -v blender)"
  fi
fi

if [[ -z "$BLENDER_BIN_VALUE" ]]; then
  os_name="$(uname -s)"
  arch_name="$(uname -m)"
  if [[ "$os_name" != "Linux" || "$arch_name" != "x86_64" ]]; then
    echo "Blender not found on PATH and auto-download only supports Linux x86_64." >&2
    echo "Set BLENDER_BIN to a Blender executable and try again." >&2
    exit 1
  fi

  blender_version="${BLENDER_VERSION:-4.2.9}"
  blender_series="$(echo "$blender_version" | awk -F. '{print $1 "." $2}')"
  cache_root="${HOME}/.cache/soleshapper"
  blender_dir="$cache_root/blender-${blender_version}-linux-x64"
  tarball_path="$cache_root/blender-${blender_version}-linux-x64.tar.xz"
  BLENDER_BIN_VALUE="$blender_dir/blender"

  if [[ ! -x "$BLENDER_BIN_VALUE" ]]; then
    mkdir -p "$cache_root"
    url="https://download.blender.org/release/Blender${blender_series}/blender-${blender_version}-linux-x64.tar.xz"
    echo "Downloading Blender ${blender_version} to $cache_root"
    curl -fL --retry 3 --retry-delay 2 -o "$tarball_path" "$url"
    tar -xf "$tarball_path" -C "$cache_root"
  fi
fi

if [[ ! -x "$BLENDER_BIN_VALUE" ]]; then
  echo "Blender binary not executable: $BLENDER_BIN_VALUE" >&2
  exit 1
fi

echo "Using Blender: $BLENDER_BIN_VALUE"
"$BLENDER_BIN_VALUE" -b --factory-startup --python "$SMOKE_SCRIPT"
