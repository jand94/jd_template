from drf_spectacular.utils import OpenApiParameter, extend_schema

COMMON_TAG = "Common"

AUDIT_LIST_PARAMETERS = [
    OpenApiParameter(
        "action",
        str,
        description="create, update, delete, access, login, login_failed, logout, or custom.",
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
