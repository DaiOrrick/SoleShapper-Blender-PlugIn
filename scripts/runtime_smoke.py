#!/usr/bin/env python3
"""Headless runtime smoke test for the SoleShapper Blender add-on.

Run with:
  blender -b --factory-startup --python scripts/runtime_smoke.py
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDON_PATH = REPO_ROOT / "__init__.py"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def cleanup_scene() -> None:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        obj.select_set(True)
    bpy.ops.object.delete(use_global=False)


def import_addon(path: Path):
    spec = importlib.util.spec_from_file_location("soleshapper_runtime_smoke", str(path))
    assert_true(spec is not None and spec.loader is not None, "Failed to load add-on module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_smoke_test() -> None:
    cleanup_scene()

    addon_mod = import_addon(ADDON_PATH)
    addon_mod.register()

    try:
        props = bpy.context.scene.sole_designer_props

        result = bpy.ops.soledesigner.load_default()
        assert_true('FINISHED' in result, f"load_default failed: {result}")
        base = bpy.data.objects.get("SoleBase")
        assert_true(base is not None and base.type == 'MESH', "SoleBase mesh missing")
        assert_true(len(base.data.vertices) > 0, "SoleBase mesh has no vertices")

        props.noise_type = 'SIMPLEX'
        props.noise_frequency = 3.0
        props.noise_amplitude = 0.01
        result = bpy.ops.soledesigner.apply_noise()
        assert_true('FINISHED' in result, f"apply_noise failed: {result}")
        deformed = bpy.data.objects.get("SoleShapper2")
        assert_true(deformed is not None and deformed.type == 'MESH', "SoleShapper2 mesh missing")

        props.mesh_scale_x = 1.10
        props.mesh_scale_y = 0.95
        props.mesh_scale_z = 1.05
        props.scale_zone = 'FULL'
        props.scale_target = 'ALL'
        result = bpy.ops.soledesigner.apply_scale()
        assert_true('FINISHED' in result, f"apply_scale failed: {result}")

        props.preset_name = "RuntimeSmoke"
        result = bpy.ops.soledesigner.save_preset()
        assert_true('FINISHED' in result, f"save_preset failed: {result}")
        result = bpy.ops.soledesigner.load_preset()
        assert_true('FINISHED' in result, f"load_preset failed: {result}")
        result = bpy.ops.soledesigner.delete_preset()
        assert_true('FINISHED' in result, f"delete_preset failed: {result}")

        with tempfile.TemporaryDirectory(prefix="soleshapper-smoke-") as tmpdir:
            tmpdir_path = Path(tmpdir)
            obj_path = tmpdir_path / "smoke.obj"
            stl_path = tmpdir_path / "smoke.stl"

            result = bpy.ops.soledesigner.export_obj(filepath=str(obj_path))
            assert_true('FINISHED' in result, f"export_obj failed: {result}")
            assert_true(obj_path.exists() and obj_path.stat().st_size > 0, "OBJ file was not written")

            result = bpy.ops.soledesigner.load_custom(filepath=str(obj_path))
            assert_true('FINISHED' in result, f"load_custom failed: {result}")

            result = bpy.ops.soledesigner.apply_noise()
            assert_true('FINISHED' in result, f"apply_noise after custom import failed: {result}")

            if hasattr(bpy.types, "EXPORT_MESH_OT_stl"):
                result = bpy.ops.soledesigner.export_stl(filepath=str(stl_path))
                assert_true('FINISHED' in result, f"export_stl failed: {result}")
                assert_true(stl_path.exists() and stl_path.stat().st_size > 0, "STL file was not written")
            else:
                print("SKIP: export_mesh.stl operator unavailable in this Blender build")

        print("RUNTIME_SMOKE_PASS")

    finally:
        addon_mod.unregister()


def main() -> int:
    try:
        run_smoke_test()
        return 0
    except Exception:
        print("RUNTIME_SMOKE_FAIL")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
