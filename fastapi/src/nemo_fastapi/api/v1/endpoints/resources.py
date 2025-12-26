"""Resource endpoints mirroring legacy Django REST routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from nemo_fastapi.porting.inventory import load_router_registry

router = APIRouter(tags=["legacy"])


def _not_implemented_payload(resource: str, item_id: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "detail": "Endpoint not yet ported from Django REST framework.",
        "resource": resource,
    }
    if item_id is not None:
        payload["id"] = item_id
    return payload


def _make_collection_handler(resource: str):
    def handler() -> dict[str, Any]:
        return _not_implemented_payload(resource)

    return handler


def _make_item_handler(resource: str):
    def handler(item_id: str) -> dict[str, Any]:
        return _not_implemented_payload(resource, item_id=item_id)

    return handler


for resource_name in load_router_registry():
    router.add_api_route(
        f"/{resource_name}",
        _make_collection_handler(resource_name),
        methods=["GET", "POST"],
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        name=f"{resource_name}_collection",
    )
    router.add_api_route(
        f"/{resource_name}/{{item_id}}",
        _make_item_handler(resource_name),
        methods=["GET", "PUT", "PATCH", "DELETE"],
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        name=f"{resource_name}_item",
    )
