"""Legacy model stubs derived from Django models for porting."""

from __future__ import annotations

from typing import Any, Dict, Type

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from nemo_fastapi.db.base import Base
from nemo_fastapi.porting.inventory import load_model_names

MODEL_REGISTRY: Dict[str, Type[Base]] = {}


def _make_model_class(name: str) -> Type[Base]:
    attributes: dict[str, Any] = {
        "__tablename__": name.lower(),
        "id": mapped_column(Integer, primary_key=True, index=True),
    }
    return type(name, (Base,), attributes)


def register_legacy_models() -> Dict[str, Type[Base]]:
    """Create placeholder SQLAlchemy models for each legacy Django model."""

    for model_name in load_model_names():
        if model_name in MODEL_REGISTRY:
            continue
        MODEL_REGISTRY[model_name] = _make_model_class(model_name)
    return MODEL_REGISTRY


register_legacy_models()
