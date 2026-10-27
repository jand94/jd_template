import re

import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User

PASSWORD = "a-long-password-99"
LOC_MEM_MAILERS = {
    "default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"},
}


@pytest.fixture(autouse=True)
def _relax_auth_throttle(settings):
    from rest_framework.throttling import SimpleRateThrottle

    rates = {
        "accounts-auth": "10000/minute",
        "accounts-register": "10000/minute",
        "accounts-reset": "10000/minute",
        "accounts-password-change": "10000/minute",
        "accounts-profile": "10000/minute",
    }
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": rates,
    }
    # DRF kopiert die Raten beim Import; die Klassen-Map muss mitgezogen werden.
    SimpleRateThrottle.THROTTLE_RATES = {
        **SimpleRateThrottle.THROTTLE_RATES,
        **rates,
    }


def _register(api_client, **overrides):
    payload = {
        "username": "ada",
        "email": "ada@example.com",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
        "first_name": "Ada",
        "terms_accepted": True,
    }
    payload.update(overrides)
    return api_client.post(reverse("accounts:register"), payload, format="json")


@pytest.mark.api
@pytest.mark.django_db
def test_register_starts_a_session_and_returns_the_profile(api_client):
    response = _register(api_client)

    assert response.status_code == 201
    assert response.json()["username"] == "ada"
    assert response.json()["email"] == "ada@example.com"
    assert response.json()["is_staff"] is False
    assert "password" not in response.json()

    me = api_client.get(reverse("accounts:me"))
    assert me.status_code == 200
    assert me.json()["first_name"] == "Ada"
    assert me.json()["terms_accepted_at"] is not None


@pytest.mark.api
@pytest.mark.django_db
def test_register_rejects_mismatched_passwords_and_missing_terms(api_client):
    mismatch = _register(api_client, password_confirm="different-password-99")
    assert mismatch.status_code == 400
    assert "password_confirm" in mismatch.json()

    terms = _register(api_client, username="grace", email="grace@example.com", terms_accepted=False)
    assert terms.status_code == 400
    assert "terms_accepted" in terms.json()


@pytest.mark.api
@pytest.mark.django_db
def test_me_requires_a_session_and_profile_updates_normalize_the_country(api_client):
    anonymous = api_client.get(reverse("accounts:me"))
    assert anonymous.status_code == 401

    _register(api_client)
    response = api_client.patch(
        reverse("accounts:me"),
        {"city": "London", "country": "gb", "email": "Ada@Example.COM"},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "London"
    assert body["country"] == "GB"
    assert body["email"] == "ada@example.com"
    assert body["is_email_verified"] is False


@pytest.mark.api
@pytest.mark.django_db
def test_login_logout_and_inactive_account(api_client):
    _register(api_client)
    api_client.post(reverse("accounts:logout"))
    assert api_client.get(reverse("accounts:me")).status_code == 401

    logged_in = api_client.post(
        reverse("accounts:login"),
        {"username": "ada", "password": PASSWORD},
        format="json",
    )
    assert logged_in.status_code == 200
    assert api_client.get(reverse("accounts:me")).status_code == 200

    wrong = api_client.post(
        reverse("accounts:login"),
        {"username": "ada", "password": "not-the-password"},
        format="json",
    )
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "Invalid username or password."

    User.objects.filter(username="ada").update(is_active=False)
    inactive = api_client.post(
        reverse("accounts:login"),
        {"username": "ada", "password": PASSWORD},
        format="json",
    )
    assert inactive.status_code == 401
    assert inactive.json()["detail"] == "Invalid username or password."


@pytest.mark.api
@pytest.mark.django_db
def test_password_change_keeps_the_session(api_client):
    _register(api_client)
    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": PASSWORD,
            "password": "another-long-password-99",
            "password_confirm": "another-long-password-99",
        },
        format="json",
    )

    assert response.status_code == 204
    assert api_client.get(reverse("accounts:me")).status_code == 200
    user = User.objects.get(username="ada")
    assert user.check_password("another-long-password-99")


@pytest.mark.api
@pytest.mark.django_db
@override_settings(MAILERS=LOC_MEM_MAILERS)
def test_password_reset_roundtrip_does_not_reveal_unknown_emails(api_client):
    _register(api_client)
    api_client.post(reverse("accounts:logout"))
    if not hasattr(mail, "outbox"):
        mail.outbox = []
    else:
        mail.outbox.clear()

    unknown = api_client.post(
        reverse("accounts:password-reset"),
        {"email": "missing@example.com"},
        format="json",
    )
    assert unknown.status_code == 204
    assert mail.outbox == []

    requested = api_client.post(
        reverse("accounts:password-reset"),
        {"email": "ada@example.com"},
        format="json",
    )
    assert requested.status_code == 204
    body = mail.outbox[0].body
    uid = re.search(r"uid: (\S+)", body).group(1)
    token = re.search(r"token: (\S+)", body).group(1)

    confirmed = api_client.post(
        reverse("accounts:password-reset-confirm"),
        {
            "uid": uid,
            "token": token,
            "password": "reset-long-password-99",
            "password_confirm": "reset-long-password-99",
        },
        format="json",
    )
    assert confirmed.status_code == 204
    assert User.objects.get(username="ada").check_password("reset-long-password-99")

    reused = api_client.post(
        reverse("accounts:password-reset-confirm"),
        {
            "uid": uid,
            "token": token,
            "password": "reset-long-password-99",
            "password_confirm": "reset-long-password-99",
        },
        format="json",
    )
    assert reused.status_code == 400


@pytest.mark.api
@pytest.mark.django_db
@override_settings(MAILERS=LOC_MEM_MAILERS)
def test_password_reset_invalidates_other_sessions(api_client):
    first = APIClient()
    second = APIClient()
    _register(first)
    second.force_login(User.objects.get(username="ada"))
    assert second.get(reverse("accounts:me")).status_code == 200

    if not hasattr(mail, "outbox"):
        mail.outbox = []
    else:
        mail.outbox.clear()

    first.post(reverse("accounts:logout"))
    first.post(reverse("accounts:password-reset"), {"email": "ada@example.com"}, format="json")
    body = mail.outbox[0].body
    uid = re.search(r"uid: (\S+)", body).group(1)
    token = re.search(r"token: (\S+)", body).group(1)

    confirmed = first.post(
        reverse("accounts:password-reset-confirm"),
        {
            "uid": uid,
            "token": token,
            "password": "reset-long-password-99",
            "password_confirm": "reset-long-password-99",
        },
        format="json",
    )
    assert confirmed.status_code == 204
    assert second.get(reverse("accounts:me")).status_code == 401


@pytest.mark.api
@pytest.mark.django_db
def test_login_requires_csrf_token_when_enforced():
    user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
    client = APIClient(enforce_csrf_checks=True)

    denied = client.post(
        reverse("accounts:login"),
        {"username": "ada", "password": PASSWORD},
        format="json",
    )
    assert denied.status_code == 403

    csrf = client.get(reverse("accounts:csrf"))
    assert csrf.status_code == 204
    token = client.cookies["csrftoken"].value
    allowed = client.post(
        reverse("accounts:login"),
        {"username": "ada", "password": PASSWORD},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert allowed.status_code == 200
    assert allowed.json()["username"] == user.username
