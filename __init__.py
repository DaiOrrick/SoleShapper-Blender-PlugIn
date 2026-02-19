"""SoleShapper extension package entrypoint.

Core implementation lives in :mod:`addon_core`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_core_module() -> ModuleType:
    # Normal extension install path: package import.
    if __package__:
        try:
            from . import addon_core

            return addon_core
        except ImportError:
            pass

    # Fallback for direct file execution in local smoke tests.
    core_path = Path(__file__).resolve().with_name("addon_core.py")
    spec = importlib.util.spec_from_file_location("soleshapper_addon_core", str(core_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load add-on core from {core_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_core = _load_core_module()
bl_info = _core.bl_info
register = _core.register
unregister = _core.unregister
