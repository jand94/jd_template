import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.unit
def test_ensure_superuser_requires_environment(monkeypatch):
    for name in (
        "DJANGO_SUPERUSER_USERNAME",
        "DJANGO_SUPERUSER_EMAIL",
        "DJANGO_SUPERUSER_PASSWORD",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(CommandError, match="DJANGO_SUPERUSER_USERNAME"):
        call_command("ensure_superuser")
