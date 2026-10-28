from django.core.cache import cache
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers import HealthSerializer, ReadySerializer


def _check_database():
    try:
        connection.ensure_connection()
    except Exception:
        return "error"
    return "ok"


def _check_cache():
    try:
        cache.set("ready-check", "ok", timeout=5)
        if cache.get("ready-check") != "ok":
            return "error"
    except Exception:
        return "error"
    return "ok"


@extend_schema(responses=HealthSerializer, tags=["System"], auth=[])
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


@extend_schema(responses=ReadySerializer, tags=["System"], auth=[])
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def ready(request):
    checks = {
        "database": _check_database(),
        "cache": _check_cache(),
    }
    available = all(value == "ok" for value in checks.values())
    return Response(
        {"status": "ok" if available else "unavailable", "checks": checks},
        status=200 if available else 503,
    )
