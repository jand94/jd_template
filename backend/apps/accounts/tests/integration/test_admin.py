import pytest
from django.contrib import admin
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.utils import timezone

from apps.accounts.admin import AccountUserAdmin
from apps.accounts.admin.filters import EmailVerifiedFilter
from apps.accounts.admin.forms import AccountUserCreationForm
from apps.accounts.models import User


def _request_for(user):
    request = RequestFactory().post("/admin/accounts/user/")
    request.user = user
    SessionMiddleware(lambda req: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda req: None).process_request(request)
    return request


@pytest.mark.integration
@pytest.mark.django_db
def test_creation_form_stores_username_email_and_password():
    form = AccountUserCreationForm(
        data={
            "username": "ada",
            "email": "Ada@Example.COM",
            "usable_password": "true",
            "password1": "a-long-password-99",
            "password2": "a-long-password-99",
        }
    )

    assert form.is_valid(), form.errors
    user = form.save()

    assert user.email == "Ada@example.com"
    assert user.check_password("a-long-password-99")
    assert user.is_staff is False


@pytest.mark.integration
@pytest.mark.django_db
def test_deactivate_users_leaves_the_acting_account_active():
    actor = User.objects.create_user("root", "root@example.com", "password", is_staff=True)
    other = User.objects.create_user("ada", "ada@example.com", "password")
    user_admin = AccountUserAdmin(User, admin.site)

    user_admin.deactivate_users(_request_for(actor), User.objects.all())

    actor.refresh_from_db()
    other.refresh_from_db()
    assert actor.is_active is True
    assert other.is_active is False


@pytest.mark.integration
@pytest.mark.django_db
def test_mark_email_verified_sets_only_missing_timestamps():
    already = timezone.now()
    verified = User.objects.create_user(
        "ada",
        "ada@example.com",
        "password",
        email_verified_at=already,
    )
    pending = User.objects.create_user("grace", "grace@example.com", "password")
    actor = User.objects.create_superuser("root", "root@example.com", "password")
    user_admin = AccountUserAdmin(User, admin.site)

    user_admin.mark_email_verified(_request_for(actor), User.objects.all())

    verified.refresh_from_db()
    pending.refresh_from_db()
    assert verified.email_verified_at == already
    assert pending.email_verified_at is not None


@pytest.mark.integration
@pytest.mark.django_db
def test_email_verified_filter_returns_verified_users():
    verified = User.objects.create_user(
        "ada",
        "ada@example.com",
        "password",
        email_verified_at=timezone.now(),
    )
    User.objects.create_user("grace", "grace@example.com", "password")
    params = {"email_verified": ["yes"]}
    user_filter = EmailVerifiedFilter(None, params, User, AccountUserAdmin)

    matched = list(user_filter.queryset(None, User.objects.all()))

    assert matched == [verified]
