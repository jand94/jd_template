from django.conf import settings
from drf_spectacular.drainage import set_override
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiParameter, extend_schema

from apps.common.api.v1.authentication import CommonSessionAuthentication

COMMON_TAG = "Common"

# Dieselbe Sitzung wie bei Accounts. Spectacular vergleicht die Klassen, nicht die Definition.
set_override(CommonSessionAuthentication, "suppress_collision_warning", True)


class CommonSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.common.api.v1.authentication.CommonSessionAuthentication"
    name = "sessionAuth"
    priority = -1

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": settings.SESSION_COOKIE_NAME,
            "description": (
                "Django session cookie. Unsafe requests from a browser also send "
                "the CSRF token in the X-CSRFToken header."
            ),
        }


AUDIT_LIST_PARAMETERS = [
    OpenApiParameter(
        "action",
        str,
        description=(
            "create, update, delete, restore, access, login, login_failed, logout, or custom."
        ),
    ),
    OpenApiParameter(
        "verb",
        str,
        description="Stable event name, for example accounts.user.update.",
    ),
    OpenApiParameter("outcome", str, description="success or failure."),
    OpenApiParameter(
        "source",
        str,
        description="api, admin, shell, task, signal, or service.",
    ),
    OpenApiParameter("actor_kind", str, description="user, anonymous, or system."),
    OpenApiParameter("actor", str, description="Primary key of the acting account."),
    OpenApiParameter("object_pk", str, description="Primary key of the audited object."),
    OpenApiParameter(
        "content_type",
        str,
        description="Target as app_label.model, for example accounts.user.",
    ),
    OpenApiParameter("request_id", str, description="X-Request-ID of the originating request."),
    OpenApiParameter(
        "correlation_id",
        str,
        description="X-Correlation-ID of the originating request.",
    ),
    OpenApiParameter("occurred_after", str, description="Inclusive ISO-8601 date or datetime."),
    OpenApiParameter("occurred_before", str, description="Inclusive ISO-8601 date or datetime."),
    OpenApiParameter(
        "q",
        str,
        description="Search actor, object, verb, message, object id, or request id.",
    ),
]


def common_schema(**kwargs):
    kwargs.setdefault("tags", [COMMON_TAG])
    return extend_schema(**kwargs)
