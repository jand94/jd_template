import contextvars
from contextlib import contextmanager
from dataclasses import dataclass, replace

_MISSING = object()
_state = contextvars.ContextVar("common_audit_context", default=None)
_suspended = contextvars.ContextVar("common_audit_suspended", default=False)


@dataclass(frozen=True)
class AuditContextState:
    """Request- oder Task-Kontext, den `record` ohne Argumente übernimmt."""

    actor: object = None
    actor_kind: str | None = None
    source: str | None = None
    ip_address: str | None = None
    user_agent: str = ""
    http_method: str = ""
    path: str = ""
    correlation_id: str = ""
    request_id: str = ""


def current_audit_state():
    return _state.get()


def current_actor():
    """Angemeldetes Konto aus dem Audit-Kontext, sonst `None`."""

    state = _state.get()
    actor = None if state is None else state.actor
    if actor is None or not getattr(actor, "is_authenticated", False):
        return None
    if not getattr(actor, "pk", None):
        return None
    return actor


def audit_is_suspended():
    return bool(_suspended.get())


@contextmanager
def audit_context(
    *,
    actor=_MISSING,
    actor_kind=_MISSING,
    source=_MISSING,
    ip_address=_MISSING,
    user_agent=_MISSING,
    http_method=_MISSING,
    path=_MISSING,
    correlation_id=_MISSING,
    request_id=_MISSING,
):
    """Setzt den Kontext für die Dauer des Blocks und stellt ihn danach wieder her."""

    previous = _state.get() or AuditContextState()
    updates = {
        "actor": actor,
        "actor_kind": actor_kind,
        "source": source,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "http_method": http_method,
        "path": path,
        "correlation_id": correlation_id,
        "request_id": request_id,
    }
    applied = {key: value for key, value in updates.items() if value is not _MISSING}
    token = _state.set(replace(previous, **applied))
    try:
        yield
    finally:
        _state.reset(token)


@contextmanager
def suspend_audit():
    """Unterdrückt automatische und explizite Audit-Einträge im Block."""

    token = _suspended.set(True)
    try:
        yield
    finally:
        _suspended.reset(token)
