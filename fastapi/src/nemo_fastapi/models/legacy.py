"""Legacy model stubs derived from Django models for porting."""

from __future__ import annotations

from typing import Any, Dict, Type

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from nemo_fastapi.db.base import Base
from nemo_fastapi.porting.inventory import (
    load_migration_model_names,
    load_migration_models,
    load_model_names,
)

MODEL_REGISTRY: Dict[str, Type[Base]] = {}

FIELD_TYPE_MAP = {
    "AutoField": Integer,
    "BigAutoField": Integer,
    "BigIntegerField": Integer,
    "BooleanField": Boolean,
    "CharField": String,
    "DateField": DateTime,
    "DateTimeField": DateTime,
    "DecimalField": Numeric,
    "EmailField": String,
    "FloatField": Float,
    "ForeignKey": Integer,
    "IntegerField": Integer,
    "JSONField": JSON,
    "OneToOneField": Integer,
    "PositiveIntegerField": Integer,
    "PositiveSmallIntegerField": Integer,
    "SlugField": String,
    "SmallIntegerField": Integer,
    "TextField": Text,
    "TimeField": DateTime,
    "UUIDField": String,
}


def _make_model_class(name: str, fields: list[tuple[str, str]] | None = None) -> Type[Base]:
    attributes: dict[str, Any] = {
        "__tablename__": name.lower(),
        "id": mapped_column(Integer, primary_key=True, index=True),
    }
    for field_name, field_type in fields or []:
        if field_name == "id" or field_name in attributes:
            continue
        column_type = FIELD_TYPE_MAP.get(field_type, String)
        attributes[field_name] = mapped_column(column_type)
    return type(name, (Base,), attributes)


def register_legacy_models() -> Dict[str, Type[Base]]:
    """Create placeholder SQLAlchemy models for each legacy Django model."""

    migration_models = load_migration_models()
    model_names = set(load_model_names())
    model_names.update(load_migration_model_names())
    for model_name in sorted(model_names):
        if model_name in MODEL_REGISTRY:
            continue
        fields = migration_models.get(model_name, [])
        MODEL_REGISTRY[model_name] = _make_model_class(model_name, fields=fields)
    return MODEL_REGISTRY


register_legacy_models()
