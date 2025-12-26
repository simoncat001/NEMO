"""Utilities for scanning the legacy Django backend for porting work."""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DJANGO_APP_PATH = REPO_ROOT / "backend" / "NEMO"
URLS_PATH = DJANGO_APP_PATH / "urls.py"
MODELS_PATH = DJANGO_APP_PATH / "models.py"
API_VIEWS_PATH = DJANGO_APP_PATH / "views" / "api.py"


def _class_base_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _collect_class_names(file_path: Path, base_names: set[str] | None = None) -> list[str]:
    if not file_path.exists():
        return []
    parsed = ast.parse(file_path.read_text(encoding="utf-8"))
    class_names: list[str] = []
    for node in parsed.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if base_names:
            bases = {_class_base_name(base) for base in node.bases}
            if not bases.intersection(base_names):
                continue
        class_names.append(node.name)
    return class_names


def load_model_names() -> list[str]:
    """Return Django model class names defined in the legacy models module."""

    return _collect_class_names(MODELS_PATH, base_names={"Model"})


def load_viewset_names() -> list[str]:
    """Return viewset class names from the legacy API module."""

    return _collect_class_names(
        API_VIEWS_PATH,
        base_names={"ModelViewSet", "ReadOnlyModelViewSet", "GenericViewSet"},
    )


def load_router_registry() -> list[str]:
    """Parse legacy router registrations to mirror available endpoints."""

    if not URLS_PATH.exists():
        return []
    urls_text = URLS_PATH.read_text(encoding="utf-8")
    matches = re.findall(r"router\\.register\\(r\"([^\"]+)\"", urls_text)
    return matches


def build_inventory() -> dict[str, list[str]]:
    """Collect legacy Django models, viewsets, and router registrations."""

    return {
        "models": load_model_names(),
        "viewsets": load_viewset_names(),
        "routes": load_router_registry(),
    }
