#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$REPO_ROOT/dist}"
MANIFEST_PATH="$REPO_ROOT/blender_manifest.toml"

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "Manifest not found: $MANIFEST_PATH" >&2
  exit 1
fi

readarray -t manifest_meta < <(python3 - "$MANIFEST_PATH" <<'PY'
import pathlib
import re
import sys

manifest = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")

def get_value(key: str) -> str:
    m = re.search(rf'(?m)^{key}\s*=\s*"([^"]+)"', manifest)
    if not m:
        raise SystemExit(f"Missing required manifest key: {key}")
    return m.group(1).strip()

print(get_value("id"))
print(get_value("version"))
PY
)

ADDON_ID="${manifest_meta[0]}"
ADDON_VERSION="${manifest_meta[1]}"
ZIP_NAME="${ADDON_ID}-${ADDON_VERSION}.zip"
ZIP_PATH="$OUT_DIR/$ZIP_NAME"

mkdir -p "$OUT_DIR"
rm -f "$ZIP_PATH" "$ZIP_PATH.sha256"

mapfile -t tracked_files < <(git -C "$REPO_ROOT" ls-files)

include_files=()
for rel_path in "${tracked_files[@]}"; do
  case "$rel_path" in
    .github/*|scripts/*|dist/*|*.zip)
      continue
      ;;
    */__pycache__/*|__pycache__/*|*.pyc)
      continue
      ;;
  esac

  abs_path="$REPO_ROOT/$rel_path"
  if [[ -f "$abs_path" ]]; then
    include_files+=("$rel_path")
  fi
done

if [[ ${#include_files[@]} -eq 0 ]]; then
  echo "No files selected for packaging." >&2
  exit 1
fi

python3 - "$REPO_ROOT" "$ZIP_PATH" "${include_files[@]}" <<'PY'
import pathlib
import sys
import zipfile

repo_root = pathlib.Path(sys.argv[1])
zip_path = pathlib.Path(sys.argv[2])
files = sys.argv[3:]

with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel in files:
        src = repo_root / rel
        if src.is_file():
            zf.write(src, arcname=rel)
PY

sha256sum "$ZIP_PATH" > "$ZIP_PATH.sha256"

echo "Built extension package: $ZIP_PATH"
echo "Checksum file: $ZIP_PATH.sha256"
