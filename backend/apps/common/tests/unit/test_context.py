import pytest

from apps.common.services import audit_context, current_actor, suspend_audit
from apps.common.services.context import audit_is_suspended, current_audit_state


class _Actor:
    is_authenticated = True
    pk = 7

    def get_username(self):
        return "ada"


@pytest.mark.unit
def test_audit_context_keeps_the_actor_and_restores_the_previous_state():
    assert current_actor() is None

    with audit_context(actor=_Actor(), source="api", request_id="req-1"):
        assert current_actor().pk == 7
        assert current_audit_state().source == "api"
        assert current_audit_state().request_id == "req-1"
        with audit_context(path="/common/v1/audit/"):
            assert current_actor().pk == 7
            assert current_audit_state().path == "/common/v1/audit/"
            assert current_audit_state().request_id == "req-1"

    assert current_actor() is None
    assert current_audit_state() is None


@pytest.mark.unit
def test_suspend_audit_is_limited_to_the_block():
    assert audit_is_suspended() is False
    with suspend_audit():
        assert audit_is_suspended() is True
    assert audit_is_suspended() is False
