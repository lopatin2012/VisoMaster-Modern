"""Startup checks for required files and downloaded models."""

import os
from pathlib import Path

MODELS_DIR = Path("model_assets")

_REQUIRED_SUPPORT = [
    "model_assets/meanshape_68.pkl",
    "model_assets/liveportrait_onnx/lip_array.pkl",
]
_PLUGIN = (
    "model_assets/grid_sample_3d_plugin.dll"
    if os.name == "nt"
    else "model_assets/libgrid_sample_3d_plugin.so"
)


def find_missing_support_files() -> list:
    """Return the list of required support files that are missing on disk."""
    required = _REQUIRED_SUPPORT + [_PLUGIN]
    return [path for path in required if not Path(path).is_file()]


def has_any_model() -> bool:
    """True if at least one ONNX model is present in model_assets/."""
    return MODELS_DIR.is_dir() and any(MODELS_DIR.glob("*.onnx"))


def find_missing_models() -> list:
    """Return local paths from ``models_list`` that are not present on disk."""
    try:
        from app.processors.models_data import models_list
    except Exception:  # pylint: disable=broad-exception-caught
        return []
    return [entry["local_path"] for entry in models_list if not Path(entry["local_path"]).is_file()]
