import json
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import class_prepared, m2m_changed, post_delete, post_save, pre_save
from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from apps.common.exceptions import AuditError
from apps.common.models.audit import AuditEvent
from apps.common.models.choices import ActorKind, AuditAction, AuditOutcome, AuditSource
from apps.common.services.context import audit_is_suspended, current_audit_state, suspend_audit
from backend.request_id import current_request_id

REDACTED = "[redacted]"
_MAX_TEXT = 2000
_MISSING = object()
_DEFAULT_EXCLUDE = frozenset({"updated_at"})
_SENSITIVE_PARTS = (
    "password",
    "passwd",
    "secret",
    "token",
    "credential",
    "session",
    "api_key",
    "private_key",
)
_exclusions = {}


def is_sensitive(name):
    lowered = str(name).lower()
    return any(part in lowered for part in _SENSITIVE_PARTS)


def to_jsonable(value, *, depth=0):
    """Wandelt Modellwerte in JSON um und kürzt übergroße Texte."""

    if value is None or isinstance(value, bool | int | float):
        if isinstance(value, bool):
            return value
        return value
    if isinstance(value, str):
        return _clip(value)
    if isinstance(value, datetime | date | time | Decimal | UUID):
        return json.loads(json.dumps(value, cls=DjangoJSONEncoder))
    if depth > 8:
        return "[truncated]"
    if isinstance(value, dict):
        return {str(key): to_jsonable(item, depth=depth + 1) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(item, depth=depth + 1) for item in value]
    name = getattr(value, "name", None)
    if name is not None and hasattr(value, "storage"):
        return _clip(name)
    try:
        return json.loads(json.dumps(value, cls=DjangoJSONEncoder))
    except TypeError:
        return _clip(str(value))


def watch(model, *, exclude=()):
    """Protokolliert create, update, delete und M2M-Änderungen von `model`."""

    if model._meta.label_lower == "common.auditevent":
        raise AuditError("AuditEvent cannot be watched.")
    label = model._meta.label_lower
    _exclusions[label] = frozenset(exclude) | _DEFAULT_EXCLUDE
    pre_save.connect(
        _remember_before,
        sender=model,
        dispatch_uid=f"common.audit.pre_save.{label}",
    )
    post_save.connect(_after_save, sender=model, dispatch_uid=f"common.audit.post_save.{label}")
    post_delete.connect(
        _after_delete,
        sender=model,
        dispatch_uid=f"common.audit.post_delete.{label}",
    )
    for field in model._meta.many_to_many:
        m2m_changed.connect(
            _make_m2m_handler(model, field),
            sender=field.remote_field.through,
            dispatch_uid=f"common.audit.m2m.{label}.{field.name}",
        )


def connect_model_auditing():
    """Beobachtet konkrete `AuditedModel`-Klassen, sobald Django sie fertigstellt."""

    class_prepared.connect(_audit_prepared_model, dispatch_uid="common.audit.class_prepared")
    from django.apps import apps

    for model in apps.get_models():
        _audit_prepared_model(sender=model)


def _audit_prepared_model(sender, **kwargs):
    if not issubclass(sender, _audited_model()) or sender._meta.abstract:
        return
    watch(sender, exclude=tuple(getattr(sender, "audit_exclude", ())))


def _audited_model():
    from apps.common.models.audited import AuditedModel

    return AuditedModel


def connect_auth_signals():
    """An- und Abmeldungen landen in der Audit-Spur, ohne das Passwort."""

    user_logged_in.connect(_on_login, dispatch_uid="common.audit.auth.login")
    user_logged_out.connect(_on_logout, dispatch_uid="common.audit.auth.logout")
    user_login_failed.connect(_on_login_failed, dispatch_uid="common.audit.auth.login_failed")


def record(
    *,
    action,
    verb="",
    actor=_MISSING,
    instance=None,
    changes=None,
    extra=None,
    outcome=AuditOutcome.SUCCESS,
    message="",
    source=_MISSING,
    correlation_id=_MISSING,
    request_id=_MISSING,
    occurred_at=None,
    ip_address=_MISSING,
    user_agent=_MISSING,
    http_method=_MISSING,
    path=_MISSING,
):
    """Schreibt ein Audit-Ereignis. Fehlende Angaben kommen aus dem Kontext."""

    if audit_is_suspended():
        return None

    try:
        action = AuditAction(action)
    except ValueError as exc:
        raise AuditError(f"Unknown audit action: {action}") from exc
    try:
        outcome = AuditOutcome(outcome)
    except ValueError as exc:
        raise AuditError(f"Unknown audit outcome: {outcome}") from exc

    state = current_audit_state()
    resolved_actor = _resolve_actor(actor, state)
    actor_kind = _actor_kind(resolved_actor, actor, state)
    linked_actor = resolved_actor if actor_kind == ActorKind.USER else None
    actor_pk = _actor_pk(linked_actor)
    actor_label = _actor_label(linked_actor)
    if linked_actor is not None and not _actor_still_stored(linked_actor):
        linked_actor = None

    content_type = None
    object_pk = ""
    object_repr = ""
    if instance is not None:
        content_type = ContentType.objects.get_for_model(instance, for_concrete_model=True)
        if getattr(instance, "pk", None) is not None:
            object_pk = str(instance.pk)[:64]
        object_repr = _clip(str(instance), limit=255)

    resolved_verb = verb or (_verb(instance, action) if instance is not None else action.value)
    resolved_source = _pick(source, None if state is None else state.source, AuditSource.SERVICE)
    try:
        resolved_source = AuditSource(resolved_source)
    except ValueError as exc:
        raise AuditError(f"Unknown audit source: {resolved_source}") from exc

    with suspend_audit():
        return AuditEvent.objects.create(
            occurred_at=occurred_at or timezone.now(),
            actor=linked_actor,
            actor_pk=actor_pk,
            actor_label=actor_label,
            actor_kind=actor_kind,
            action=action,
            verb=_clip(resolved_verb, limit=128),
            content_type=content_type,
            object_pk=object_pk,
            object_repr=object_repr,
            changes=normalize_changes(changes),
            extra=sanitize_extra(extra),
            outcome=outcome,
            message=_clip(message or "", limit=4000),
            request_id=_request_id(request_id, state),
            correlation_id=_clip(
                _pick(correlation_id, "" if state is None else state.correlation_id, ""),
                limit=64,
            ),
            ip_address=_ip(_pick(ip_address, None if state is None else state.ip_address, None)),
            user_agent=_clip(
                _pick(user_agent, "" if state is None else state.user_agent, ""),
                limit=512,
            ),
            http_method=_clip(
                _pick(http_method, "" if state is None else state.http_method, ""),
                limit=16,
            ),
            path=_clip(_pick(path, "" if state is None else state.path, ""), limit=512),
            source=resolved_source,
        )


def normalize_changes(changes):
    if changes is None:
        return []
    rows = _change_rows(changes)
    normalized = []
    for field, old, new in rows:
        name = str(field)[:128]
        if is_sensitive(name):
            old = None if old is None else REDACTED
            new = None if new is None else REDACTED
        else:
            old = None if old is None else to_jsonable(old)
            new = None if new is None else to_jsonable(new)
        normalized.append({"field": name, "old": old, "new": new})
    return normalized


def sanitize_extra(payload):
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise AuditError("extra must be a dictionary.")
    clean = {}
    for key, value in payload.items():
        name = str(key)
        clean[name] = REDACTED if is_sensitive(name) else to_jsonable(value)
    return clean


def _change_rows(changes):
    if isinstance(changes, dict):
        rows = []
        for field, value in changes.items():
            if isinstance(value, dict) and {"old", "new"} <= set(value):
                rows.append((field, value.get("old"), value.get("new")))
                continue
            if isinstance(value, list | tuple) and len(value) == 2:
                rows.append((field, value[0], value[1]))
                continue
            raise AuditError("A change dictionary maps a field to {'old', 'new'} or [old, new].")
        return rows
    if not isinstance(changes, list | tuple):
        raise AuditError("changes must be a list or a dictionary.")
    rows = []
    for item in changes:
        if not isinstance(item, dict) or "field" not in item:
            raise AuditError("Each change needs a field, old, and new value.")
        rows.append((item.get("field"), item.get("old"), item.get("new")))
    return rows


def _remember_before(sender, instance, raw=False, **kwargs):
    if raw or audit_is_suspended() or getattr(instance, "_skip_audit", False):
        return
    if instance.pk and not instance._state.adding:
        previous = sender._base_manager.filter(pk=instance.pk).first()
        instance._audit_before = None if previous is None else _state_of(previous)
    else:
        instance._audit_before = None


def _after_save(sender, instance, created, raw=False, **kwargs):
    if raw or audit_is_suspended() or getattr(instance, "_skip_audit", False):
        return
    after = _state_of(instance)
    if created:
        changes = _changes_from_empty(after)
        action = AuditAction.CREATE
    else:
        before = getattr(instance, "_audit_before", None) or ({}, {})
        changes = _changes_between(before, after)
        if not changes:
            return
        action = AuditAction.UPDATE
    record(action=action, verb=_verb(instance, action), instance=instance, changes=changes)


def _after_delete(sender, instance, **kwargs):
    if audit_is_suspended() or getattr(instance, "_skip_audit", False):
        return
    public, secrets = _state_of(instance)
    changes = [{"field": field, "old": value, "new": None} for field, value in public.items()]
    changes.extend({"field": field, "old": REDACTED, "new": None} for field in secrets)
    record(
        action=AuditAction.DELETE,
        verb=_verb(instance, AuditAction.DELETE),
        instance=instance,
        changes=changes,
    )


def _make_m2m_handler(model, field):
    cache_name = f"_audit_m2m_{field.name}"

    def handler(sender, instance, action, reverse, pk_set, **kwargs):
        if audit_is_suspended():
            return
        if not reverse:
            _forward_m2m(model, field, instance, action, cache_name)
            return
        if action not in {"post_add", "post_remove"} or not pk_set:
            return
        for object_pk in pk_set:
            target = model._base_manager.filter(pk=object_pk).first()
            if target is None:
                continue
            _record_reverse_m2m(model, field, target, instance.pk, action)

    return handler


def _forward_m2m(model, field, instance, action, cache_name):
    if not isinstance(instance, model):
        return
    relation = getattr(instance, field.name)
    if action in {"pre_add", "pre_remove", "pre_clear"}:
        setattr(instance, cache_name, set(relation.values_list("pk", flat=True)))
        return
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    before = getattr(instance, cache_name, None)
    if before is None:
        return
    after = set(relation.values_list("pk", flat=True))
    if before == after:
        return
    record(
        action=AuditAction.UPDATE,
        verb=_verb(instance, AuditAction.UPDATE),
        instance=instance,
        changes=[_relation_change(field, before, after)],
    )


def _record_reverse_m2m(model, field, target, related_pk, action):
    after = set(getattr(target, field.name).values_list("pk", flat=True))
    if action == "post_add":
        before = after - {related_pk}
    else:
        before = after | {related_pk}
    if before == after:
        return
    record(
        action=AuditAction.UPDATE,
        verb=_verb(target, AuditAction.UPDATE),
        instance=target,
        changes=[_relation_change(field, before, after)],
    )


def _relation_change(field, before, after):
    if is_sensitive(field.name):
        return {"field": field.name, "old": REDACTED, "new": REDACTED}
    return {
        "field": field.name,
        "old": sorted(str(pk) for pk in before),
        "new": sorted(str(pk) for pk in after),
    }


def _state_of(instance):
    exclude = _exclusions.get(instance._meta.label_lower, _DEFAULT_EXCLUDE)
    public = {}
    secrets = {}
    for field in instance._meta.concrete_fields:
        if not field.concrete or field.many_to_many:
            continue
        if field.name in exclude:
            continue
        raw = _raw_value(instance, field)
        if is_sensitive(field.name):
            secrets[field.name] = raw
        else:
            public[field.name] = to_jsonable(raw)
    return public, secrets


def _raw_value(instance, field):
    if isinstance(field, models.FileField):
        stored = getattr(instance, field.name)
        return "" if not stored else stored.name
    if field.is_relation:
        return getattr(instance, field.attname)
    return field.value_from_object(instance)


def _changes_from_empty(state):
    public, secrets = state
    changes = [{"field": name, "old": None, "new": value} for name, value in public.items()]
    changes.extend({"field": name, "old": None, "new": REDACTED} for name in secrets)
    return _sorted(changes)


def _changes_between(before, after):
    public_changes = []
    fields = list(dict.fromkeys([*before[0].keys(), *after[0].keys()]))
    for field in fields:
        old = before[0].get(field)
        new = after[0].get(field)
        if old != new:
            public_changes.append({"field": field, "old": old, "new": new})
    secret_names = set(before[1]) | set(after[1])
    for name in sorted(secret_names):
        old_raw = before[1].get(name, _MISSING)
        new_raw = after[1].get(name, _MISSING)
        if old_raw == new_raw:
            continue
        public_changes.append(
            {
                "field": name,
                "old": None if old_raw is _MISSING else REDACTED,
                "new": None if new_raw is _MISSING else REDACTED,
            }
        )
    return _sorted(public_changes)


def _sorted(changes):
    return sorted(changes, key=lambda item: item["field"])


def _on_login(sender, request, user, **kwargs):
    record(
        action=AuditAction.LOGIN,
        verb="auth.login",
        actor=user,
        instance=user,
        source=_signal_source(),
    )


def _on_logout(sender, request, user, **kwargs):
    record(
        action=AuditAction.LOGOUT,
        verb="auth.logout",
        actor=user,
        instance=user,
        source=_signal_source(),
    )


def _on_login_failed(sender, credentials, request=None, **kwargs):
    safe = {}
    for key, value in (credentials or {}).items():
        if is_sensitive(key):
            continue
        safe[str(key)] = value if isinstance(value, str | int) else str(value)
    record(
        action=AuditAction.LOGIN_FAILED,
        verb="auth.login_failed",
        outcome=AuditOutcome.FAILURE,
        message="Login failed.",
        extra=safe,
        source=_signal_source(),
    )


def _signal_source():
    state = current_audit_state()
    if state is not None and state.source:
        return state.source
    return AuditSource.SIGNAL


def _resolve_actor(actor, state):
    if actor is not _MISSING:
        return _unwrap_actor(actor)
    if state is None:
        return None
    return _unwrap_actor(state.actor)


def _unwrap_actor(actor):
    """Löst den Lazy-User der Middleware auf das echte Modell auf."""

    if not isinstance(actor, SimpleLazyObject):
        return actor
    getattr(actor, "is_authenticated", False)
    return getattr(actor, "_wrapped", actor)


def _actor_kind(actor, passed, state):
    if actor is not None and getattr(actor, "is_authenticated", False):
        return ActorKind.USER
    if actor is not None and not getattr(actor, "is_authenticated", True):
        return ActorKind.ANONYMOUS
    if passed is _MISSING and state is not None and state.actor_kind:
        return state.actor_kind
    return ActorKind.SYSTEM


def _actor_still_stored(actor):
    pk = getattr(actor, "pk", None)
    manager = getattr(actor.__class__, "_base_manager", None)
    if pk is None or manager is None:
        return False
    return manager.filter(pk=pk).exists()


def _actor_pk(actor):
    if actor is None or not getattr(actor, "is_authenticated", False):
        return ""
    pk = getattr(actor, "pk", None)
    return "" if pk is None else str(pk)[:64]


def _actor_label(actor):
    if actor is None:
        return ""
    for name in ("get_display_name", "get_username"):
        method = getattr(actor, name, None)
        if not callable(method):
            continue
        label = (method() or "").strip()
        if label:
            return _clip(label, limit=255)
    return _clip(str(actor), limit=255)


def _verb(instance, action):
    action_value = action.value if isinstance(action, AuditAction) else str(action)
    return f"{instance._meta.label_lower}.{action_value}"


def _request_id(passed, state):
    if passed is not _MISSING and passed is not None:
        return _clip(str(passed), limit=64)
    if state is not None and state.request_id:
        return _clip(state.request_id, limit=64)
    current = current_request_id()
    if current in ("", "-"):
        return ""
    return _clip(current, limit=64)


def _pick(passed, from_state, default):
    if passed is not _MISSING:
        return passed
    if from_state is None:
        return default
    return from_state


def _ip(value):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        import ipaddress

        ipaddress.ip_address(text)
    except ValueError:
        return None
    return text


def _clip(value, *, limit=_MAX_TEXT):
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    marker = "…[truncated]"
    return text[: max(limit - len(marker), 0)] + marker
