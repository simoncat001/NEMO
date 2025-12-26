"""SQLAlchemy model exports for FastAPI."""

from nemo_fastapi.models.legacy import MODEL_REGISTRY, register_legacy_models

__all__ = ["MODEL_REGISTRY", "register_legacy_models"]
