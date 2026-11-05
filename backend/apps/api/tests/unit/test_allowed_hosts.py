import pytest

from backend.settings import allowed_hosts


@pytest.mark.unit
def test_allowed_hosts_keeps_internal_names_beside_the_public_host(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")

    assert allowed_hosts() == ["example.com", "localhost", "127.0.0.1", "backend"]


@pytest.mark.unit
def test_allowed_hosts_uses_internal_names_when_unset(monkeypatch):
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)

    assert allowed_hosts() == ["localhost", "127.0.0.1", "backend"]


@pytest.mark.unit
def test_allowed_hosts_lists_each_name_once(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "backend, example.com, backend")

    assert allowed_hosts() == ["backend", "example.com", "localhost", "127.0.0.1"]
