import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def locmem_email(settings):
    settings.MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
        },
    }


@pytest.fixture
def api_client():
    return APIClient()
