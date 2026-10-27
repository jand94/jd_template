import pytest
from django.conf import settings
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIRequestFactory

from apps.accounts.api.v1.permissions import IsActiveAccount


@pytest.mark.unit
def test_active_account_permission_rejects_anonymous_and_inactive_users():
    permission = IsActiveAccount()
    factory = APIRequestFactory()
    request = factory.get("/accounts/v1/me/")

    request.user = type("Anonymous", (), {"is_authenticated": False, "is_active": False})()
    assert permission.has_permission(request, None) is False

    request.user = type("Inactive", (), {"is_authenticated": True, "is_active": False})()
    assert permission.has_permission(request, None) is False

    request.user = type("Active", (), {"is_authenticated": True, "is_active": True})()
    assert permission.has_permission(request, None) is True


@pytest.mark.unit
def test_openapi_schema_lists_account_operations():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    assert schema["info"]["title"] == settings.API_TITLE
    assert schema["info"]["description"] == settings.API_DESCRIPTION
    assert schema["info"]["version"] == settings.API_VERSION

    assert "/accounts/v1/register/" in paths
    assert "/accounts/v1/login/" in paths
    assert "/accounts/v1/logout/" in paths
    assert "/accounts/v1/me/" in paths
    assert "/accounts/v1/password/change/" in paths
    assert "/accounts/v1/password/reset/" in paths
    assert "/accounts/v1/password/reset/confirm/" in paths
    assert paths["/accounts/v1/me/"]["get"]["tags"] == ["Accounts"]
    assert paths["/accounts/v1/me/"]["patch"]["tags"] == ["Accounts"]
    assert "post" in paths["/accounts/v1/register/"]
