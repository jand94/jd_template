import pytest
from django.db import IntegrityError, transaction

from apps.accounts.models import User


@pytest.mark.integration
@pytest.mark.django_db
def test_create_user_stores_profile_and_normalizes_country():
    created = User.objects.create_user(
        username="ada",
        email="Ada@Example.COM",
        password="password",
        first_name="Ada",
        last_name="Lovelace",
        street="St James's Square",
        house_number="12",
        postal_code="SW1Y 4LB",
        city="London",
        country="gb",
    )

    stored = User.objects.get(username="ada")

    assert stored.pk == created.pk
    assert stored.email == "Ada@example.com"
    assert stored.country == "GB"
    assert stored.check_password("password")
    assert stored.is_staff is False
    assert stored.is_superuser is False
    assert stored.formatted_address().splitlines()[0] == "St James's Square 12"


@pytest.mark.integration
@pytest.mark.django_db
def test_email_must_be_unique():
    User.objects.create_user("ada", "ada@example.com", "password")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user("ada2", "ada@example.com", "password")


@pytest.mark.integration
@pytest.mark.django_db
def test_email_cannot_be_blank():
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create(username="blank", email="")


@pytest.mark.integration
@pytest.mark.django_db
def test_create_superuser_sets_staff_flags():
    user = User.objects.create_superuser(
        username="root",
        email="root@example.com",
        password="password",
    )

    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True
