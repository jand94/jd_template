from datetime import date, datetime, timezone as datetime_timezone

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.admin import AccountUserAdmin
from apps.accounts.models import AbstractUser, User
from apps.accounts.models.validators import validate_timezone_name


def _user(**kwargs):
    values = {"username": "ada", "email": "ada@example.com"}
    values.update(kwargs)
    return User(**values)


@pytest.mark.unit
def test_auth_user_model_is_accounts_user():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert get_user_model() is User
    assert AbstractUser._meta.abstract is True
    assert User._meta.swappable == "AUTH_USER_MODEL"
    assert User._meta.get_field("email").unique is True
    assert User._meta.get_field("email").blank is False


@pytest.mark.unit
def test_get_full_name_joins_present_name_parts():
    user = _user(title="Dr.", first_name="Ada", middle_name="", last_name="Lovelace")

    assert user.get_full_name() == "Dr. Ada Lovelace"


@pytest.mark.unit
def test_short_and_display_name_prefer_the_preferred_name():
    user = _user(
        title="Dr.",
        first_name="Augusta",
        middle_name="Ada",
        last_name="Lovelace",
        preferred_name="Ada",
    )

    assert user.get_short_name() == "Ada"
    assert user.get_display_name() == "Ada Lovelace"
    assert str(user) == "Ada Lovelace (ada)"


@pytest.mark.unit
def test_display_name_uses_preferred_name_without_a_last_name():
    user = _user(preferred_name="Ada", first_name="Augusta", last_name="")

    assert user.get_display_name() == "Ada"


@pytest.mark.unit
def test_display_name_falls_back_to_username():
    user = _user()

    assert user.get_short_name() == "ada"
    assert user.get_display_name() == "ada"
    assert str(user) == "ada"


@pytest.mark.unit
def test_formatted_address_skips_blank_lines():
    user = _user(
        street="St James's Square",
        house_number="12",
        address_line2="",
        postal_code="SW1Y 4LB",
        city="London",
        region="",
        country="GB",
    )

    assert user.formatted_address() == "St James's Square 12\nSW1Y 4LB London\nGB"


@pytest.mark.unit
def test_clean_normalizes_email_and_country_codes():
    user = _user(email="Ada@Example.COM", country="de", nationality="gb")

    user.clean()

    assert user.email == "Ada@example.com"
    assert user.country == "DE"
    assert user.nationality == "GB"


@pytest.mark.unit
def test_clean_rejects_a_future_date_of_birth():
    user = _user(date_of_birth=timezone.localdate().replace(year=timezone.localdate().year + 1))

    with pytest.raises(ValidationError) as exc_info:
        user.clean()

    assert "date_of_birth" in exc_info.value.message_dict


@pytest.mark.unit
def test_age_counts_completed_years(monkeypatch):
    monkeypatch.setattr(
        "apps.accounts.models.user.timezone.localdate",
        lambda: date(2026, 6, 15),
    )
    user = _user(date_of_birth=date(2000, 6, 15))

    assert user.age == 26

    user.date_of_birth = date(2000, 6, 16)
    assert user.age == 25

    user.date_of_birth = None
    assert user.age is None


@pytest.mark.unit
def test_verification_flags_follow_timestamps():
    user = _user()

    assert user.is_email_verified is False
    assert user.is_phone_verified is False

    user.email_verified_at = datetime(2026, 1, 1, tzinfo=datetime_timezone.utc)
    user.phone_verified_at = datetime(2026, 1, 2, tzinfo=datetime_timezone.utc)

    assert user.is_email_verified is True
    assert user.is_phone_verified is True


@pytest.mark.unit
def test_create_user_requires_an_email():
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user("ada", "  ", "password")


@pytest.mark.unit
def test_timezone_validator_accepts_blank_and_iana_names():
    validate_timezone_name("")
    validate_timezone_name("Europe/Berlin")


@pytest.mark.unit
def test_personal_fields_reject_invalid_values():
    user = _user(
        phone="telefon",
        country="DEU",
        nationality="D",
        language="deutsch",
        timezone="Berlin",
    )

    with pytest.raises(ValidationError) as exc_info:
        user.clean_fields()

    errors = exc_info.value.message_dict
    assert "phone" in errors
    assert "country" in errors
    assert "nationality" in errors
    assert "language" in errors
    assert "timezone" in errors


@pytest.mark.unit
def test_admin_exposes_profile_contact_and_address():
    fields = []
    for _label, options in AccountUserAdmin.fieldsets:
        for field in options["fields"]:
            if isinstance(field, tuple):
                fields.extend(field)
            else:
                fields.append(field)
    add_fields = AccountUserAdmin.add_fieldsets[0][1]["fields"]

    assert {"street", "city", "date_of_birth", "phone", "language"} <= set(fields)
    assert "email" in add_fields
    assert "usable_password" in add_fields
