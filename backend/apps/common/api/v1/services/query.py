from datetime import datetime, time

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from apps.common.exceptions import AuditQueryError
from apps.common.models.choices import ActorKind, AuditAction, AuditOutcome, AuditSource


def filter_audit_events(queryset, params):
    """Schränkt die Audit-Spur auf die übergebenen Query-Parameter ein."""

    queryset = _choice(queryset, params, "action", AuditAction, "action")
    queryset = _choice(queryset, params, "outcome", AuditOutcome, "outcome")
    queryset = _choice(queryset, params, "source", AuditSource, "source")
    queryset = _choice(queryset, params, "actor_kind", ActorKind, "actor_kind")
    queryset = _exact(queryset, params, "verb", "verb")
    queryset = _exact(queryset, params, "object_pk", "object_pk")
    queryset = _exact(queryset, params, "request_id", "request_id")
    queryset = _exact(queryset, params, "correlation_id", "correlation_id")

    actor = _text(params.get("actor"))
    if actor:
        queryset = queryset.filter(actor_id=_actor_pk(actor))

    content_type = _text(params.get("content_type"))
    if content_type:
        queryset = queryset.filter(content_type=_content_type(content_type))

    occurred_after = _timestamp(params.get("occurred_after"), end=False)
    if occurred_after is not None:
        queryset = queryset.filter(occurred_at__gte=occurred_after)
    occurred_before = _timestamp(params.get("occurred_before"), end=True)
    if occurred_before is not None:
        queryset = queryset.filter(occurred_at__lte=occurred_before)

    term = _text(params.get("q"))
    if term:
        queryset = queryset.filter(
            Q(actor_label__icontains=term)
            | Q(object_repr__icontains=term)
            | Q(verb__icontains=term)
            | Q(message__icontains=term)
            | Q(object_pk__icontains=term)
            | Q(request_id__icontains=term)
        )
    return queryset


def _choice(queryset, params, name, enum, field):
    value = _text(params.get(name))
    if not value:
        return queryset
    if value not in enum.values:
        allowed = ", ".join(enum.values)
        raise AuditQueryError(f"{name} must be one of: {allowed}.")
    return queryset.filter(**{field: value})


def _exact(queryset, params, name, field):
    value = _text(params.get(name))
    if not value:
        return queryset
    return queryset.filter(**{field: value})


def _actor_pk(value):
    field = get_user_model()._meta.pk
    try:
        return field.to_python(value)
    except (ValidationError, ValueError, TypeError) as exc:
        raise AuditQueryError("actor must be a user id.") from exc


def _content_type(value):
    app_label, separator, model = value.partition(".")
    if not separator or not app_label or not model or "." in model:
        raise AuditQueryError("content_type must be app_label.model.")
    try:
        return ContentType.objects.get_by_natural_key(app_label, model)
    except ContentType.DoesNotExist as exc:
        raise AuditQueryError(f"Unknown content type: {value}.") from exc


def _timestamp(value, *, end):
    text = _text(value)
    if not text:
        return None
    parsed = parse_datetime(text)
    if parsed is None:
        day = parse_date(text)
        if day is None:
            name = "occurred_before" if end else "occurred_after"
            raise AuditQueryError(f"{name} is not a valid date.")
        clock = time.max if end else time.min
        parsed = datetime.combine(day, clock)
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _text(value):
    if value is None:
        return ""
    return str(value).strip()
