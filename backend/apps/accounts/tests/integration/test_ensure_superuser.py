import pytest
from django.core.management import call_command

from apps.accounts.models import User


def _set_superuser_env(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "root")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "Root@Example.COM")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "password")


@pytest.mark.integration
@pytest.mark.django_db
def test_ensure_superuser_creates_an_active_superuser(monkeypatch):
    _set_superuser_env(monkeypatch)

    call_command("ensure_superuser")

    user = User.objects.get(username="root")
    assert user.email == "Root@example.com"
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True
    assert user.check_password("password")


@pytest.mark.integration
@pytest.mark.django_db
def test_ensure_superuser_does_not_create_a_second_account(monkeypatch):
    _set_superuser_env(monkeypatch)

    call_command("ensure_superuser")
    call_command("ensure_superuser")

    assert User.objects.filter(username="root").count() == 1
