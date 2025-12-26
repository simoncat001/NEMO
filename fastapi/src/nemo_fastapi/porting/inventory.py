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
MIGRATIONS_PATH = DJANGO_APP_PATH / "migrations"


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
        "migration_models": load_migration_model_names(),
        "viewsets": load_viewset_names(),
        "routes": load_router_registry(),
    }


def _extract_constant(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    return None


def _extract_field_type(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
    return None


def _collect_migration_models(file_path: Path) -> dict[str, list[tuple[str, str]]]:
    parsed = ast.parse(file_path.read_text(encoding="utf-8"))
    models: dict[str, list[tuple[str, str]]] = {}
    for node in ast.walk(parsed):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "CreateModel":
            continue
        model_name = None
        fields: list[tuple[str, str]] = []
        for keyword in node.keywords:
            if keyword.arg == "name":
                model_name = _extract_constant(keyword.value)
            if keyword.arg == "fields" and isinstance(keyword.value, ast.List):
                for field_node in keyword.value.elts:
                    if not isinstance(field_node, ast.Tuple) or len(field_node.elts) < 2:
                        continue
                    field_name = _extract_constant(field_node.elts[0])
                    field_type = _extract_field_type(field_node.elts[1])
                    if field_name and field_type:
                        fields.append((field_name, field_type))
        if model_name:
            models.setdefault(model_name, []).extend(fields)
    return models


def load_migration_models() -> dict[str, list[tuple[str, str]]]:
    """Return model fields discovered in Django migration files."""

    if not MIGRATIONS_PATH.exists():
        return {}
    models: dict[str, list[tuple[str, str]]] = {}
    for migration_file in MIGRATIONS_PATH.glob("*.py"):
        if migration_file.name == "__init__.py":
            continue
        for model_name, fields in _collect_migration_models(migration_file).items():
            models.setdefault(model_name, []).extend(fields)
    return models


def load_migration_model_names() -> list[str]:
    """Return model names discovered in Django migration files."""

    return sorted(load_migration_models().keys())
