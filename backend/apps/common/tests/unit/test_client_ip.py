import pytest

from apps.common.middleware import client_ip
from apps.common.services import audit_context, current_actor


class _Request:
    def __init__(self, meta):
        self.META = meta


class _Actor:
    is_authenticated = True
    pk = None


@pytest.mark.unit
def test_client_ip_prefers_a_valid_forwarded_address_and_ignores_garbage():
    forwarded = _Request(
        {
            "HTTP_X_FORWARDED_FOR": "spoofed, 198.51.100.8",
            "REMOTE_ADDR": "10.0.0.1",
        }
    )
    assert client_ip(forwarded) == "198.51.100.8"

    invalid = _Request(
        {
            "HTTP_X_REAL_IP": "not-an-ip",
            "HTTP_X_FORWARDED_FOR": "also-bad",
            "REMOTE_ADDR": "",
        }
    )
    assert client_ip(invalid) is None


@pytest.mark.unit
def test_current_actor_ignores_an_unsaved_account():
    with audit_context(actor=_Actor()):
        assert current_actor() is None
