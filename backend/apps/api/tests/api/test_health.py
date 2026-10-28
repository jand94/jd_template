import logging

import pytest
from django.urls import reverse

from backend.request_id import RequestIdFilter


@pytest.mark.api
@pytest.mark.django_db
def test_health_returns_ok_without_a_session(api_client):
    response = api_client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.api
@pytest.mark.django_db
def test_ready_checks_database_and_cache(api_client):
    response = api_client.get(reverse("ready"))

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": {"database": "ok", "cache": "ok"},
    }


@pytest.mark.api
@pytest.mark.django_db
def test_ready_hides_cache_failures(api_client, monkeypatch):
    def fail(*args, **kwargs):
        raise ConnectionError("redis password leaked")

    monkeypatch.setattr("django.core.cache.cache.set", fail)

    response = api_client.get(reverse("ready"))
    body = response.content.decode()

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["checks"]["cache"] == "error"
    assert "password" not in body


@pytest.mark.api
def test_health_echoes_a_safe_request_id(api_client):
    response = api_client.get(reverse("health"), HTTP_X_REQUEST_ID="trace-1")

    assert response.status_code == 200
    assert response["X-Request-ID"] == "trace-1"


@pytest.mark.api
def test_request_log_keeps_the_request_id(api_client, caplog):
    with caplog.at_level(logging.WARNING, logger="django.request"):
        response = api_client.get(reverse("accounts:me"), HTTP_X_REQUEST_ID="trace-1")

    assert response.status_code == 401
    records = [record for record in caplog.records if record.name == "django.request"]
    assert records
    log_filter = RequestIdFilter()
    assert all(log_filter.filter(record) and record.request_id == "trace-1" for record in records)


@pytest.mark.api
def test_health_replaces_an_unsafe_request_id(api_client):
    response = api_client.get(reverse("health"), HTTP_X_REQUEST_ID="bad id\n")

    assert response.status_code == 200
    assert response["X-Request-ID"] != "bad id\n"
    assert response["X-Request-ID"]
