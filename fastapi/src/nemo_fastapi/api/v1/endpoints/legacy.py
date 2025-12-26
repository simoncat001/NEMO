"""Placeholder endpoints for porting legacy Django REST API resources."""

from fastapi import APIRouter, status

router = APIRouter(tags=["legacy"])


@router.api_route(
    "/legacy/{resource}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
def legacy_placeholder(resource: str) -> dict[str, str]:
    return {
        "detail": "Endpoint not yet ported from Django REST framework.",
        "resource": resource,
    }
