from __future__ import annotations

from typing import Any, Mapping, Optional

from rest_framework.response import Response

from NEMO.serializers import serialize_context


def render_api(
    request,
    template_name: Optional[str] = None,
    context: Optional[Mapping[str, Any]] = None,
    status: Optional[int] = None,
    **kwargs,
):
    payload = serialize_context(context or {})
    return Response(payload, status=status)
