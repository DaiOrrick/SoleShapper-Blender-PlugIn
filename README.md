# SoleShapper - Blender Plug-In

SoleShapper is a Blender plug-in designed specifically for shoe designers who need intuitive, art-directed control over shaping sole meshes through procedural methods rather than manual sculpting.

## Features

- Default sole mesh baked into the plugin (no external files needed)
- Load custom OBJ meshes for any sole shape
- Procedural noise deformation applied via vertex normals
- Zone masking for targeted deformation
- Export deformed soles as STL or OBJ
- Reset to base mesh and iterate freely

## Requirements

- Blender 4.2.0 or later (tested with Blender 5.x)

## Installation

1. Build a release zip:

   ```bash
   bash scripts/build_extension_zip.sh
   ```

2. Open Blender and go to **Edit > Preferences**.
3. Open the **Get Extensions** section and choose **Install from Disk...**.
4. Select `dist/soleshapper-<version>.zip`.
5. Enable **SoleShapper** in the Extensions/Add-ons list.

## Usage

1. Press **N** in the 3D Viewport to open the side panel
2. Look for the **SoleShapper2** tab
3. Click **Load Default Sole** or **Load Custom OBJ**
4. Adjust noise parameters (scale, strength, seed, etc.)
5. Click **Apply Noise Deformation**
6. Reset to base and try again any time

## Runtime Smoke Test

Run a headless end-to-end smoke test of the add-on:

```bash
bash scripts/run_runtime_smoke.sh
```

Options:

- Use a specific Blender binary:

  ```bash
  BLENDER_BIN=/path/to/blender bash scripts/run_runtime_smoke.sh
  ```

- Override portable Blender version (Linux x86_64 auto-download path):

  ```bash
  BLENDER_VERSION=4.2.9 bash scripts/run_runtime_smoke.sh
  ```

The test exercises add-on registration, default mesh load, noise/scale operators,
preset save/load/delete, OBJ export/import, and STL export.

GitHub CI runs the same smoke test on pull requests and pushes to `main` via
`.github/workflows/runtime-smoke.yml`.

## Release Packaging

Build a distributable extension zip locally:

```bash
bash scripts/build_extension_zip.sh
```

Output:

- `dist/soleshapper-<version>.zip`
- `dist/soleshapper-<version>.zip.sha256`

Automated tag release build:

1. Bump `version` in `blender_manifest.toml`.
2. Keep `bl_info["version"]` in `addon_core.py` in sync (or run `python3 scripts/check_version_consistency.py`).
3. Create and push a tag, for example:

   ```bash
   git tag v2.0.1
   git push origin v2.0.1
   ```

4. GitHub Actions workflow `.github/workflows/release-extension.yml` builds the zip
   and attaches it to the GitHub Release for that tag.

## Troubleshooting

If the add-on tab is missing in the 3D Viewport sidebar:

1. Confirm the add-on is enabled in **Edit > Preferences > Add-ons**.
2. In the 3D Viewport, press **N** to open the sidebar and look for the
   **SoleShapper2** tab.
3. If it still does not appear, disable/re-enable the add-on and restart Blender.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
