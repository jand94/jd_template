from rest_framework.permissions import BasePermission
from rest_framework.throttling import ScopedRateThrottle


class CanViewAuditTrail(BasePermission):
    """Erlaubt aktiven Konten mit dem Recht `common.view_auditevent` den Zugriff."""

    message = "You do not have permission to view the audit trail."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        return user.has_perm("common.view_auditevent")


class AuditReadThrottle(ScopedRateThrottle):
    scope = "common-audit"

    def allow_request(self, request, view):
        if getattr(view, self.scope_attr, None) is None:
            view.throttle_scope = self.scope
        return super().allow_request(request, view)
