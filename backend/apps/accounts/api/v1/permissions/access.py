from rest_framework.permissions import BasePermission
from rest_framework.throttling import ScopedRateThrottle


class IsActiveAccount(BasePermission):
    """Erlaubt nur angemeldeten und aktiven Konten den Zugriff."""

    message = "This account is inactive."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(user.is_active)


class AccountsAuthThrottle(ScopedRateThrottle):
    scope = "accounts-auth"

    def allow_request(self, request, view):
        if getattr(view, self.scope_attr, None) is None:
            view.throttle_scope = self.scope
        return super().allow_request(request, view)
