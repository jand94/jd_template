import ipaddress
import re

from apps.common.models.choices import ActorKind, AuditSource
from apps.common.services.context import audit_context

_SAFE_CORRELATION = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def client_ip(request):
    """Client-Adresse, wie der vorgeschaltete Proxy sie setzt."""

    candidates = []
    real = request.META.get("HTTP_X_REAL_IP", "").strip()
    if real:
        candidates.append(real)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    parts = [part.strip() for part in forwarded.split(",") if part.strip()]
    if parts:
        candidates.append(parts[-1])
    remote = request.META.get("REMOTE_ADDR", "").strip()
    if remote:
        candidates.append(remote)
    for candidate in candidates:
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            continue
        return candidate
    return None


class AuditContextMiddleware:
    """Bindet Konto, Quelle und Request-Daten an den Audit-Kontext."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            actor = user
            actor_kind = ActorKind.USER
        else:
            actor = None
            actor_kind = ActorKind.ANONYMOUS
        source = AuditSource.ADMIN if request.path.startswith("/admin/") else AuditSource.API
        correlation = request.headers.get("X-Correlation-ID", "").strip()
        if not _SAFE_CORRELATION.fullmatch(correlation):
            correlation = ""
        request_id = getattr(request, "request_id", "") or ""
        with audit_context(
            actor=actor,
            actor_kind=actor_kind,
            source=source,
            ip_address=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            http_method=request.method,
            path=request.path,
            correlation_id=correlation,
            request_id=request_id,
        ):
            return self.get_response(request)
