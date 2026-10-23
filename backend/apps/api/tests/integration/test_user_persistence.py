import pytest
from django.contrib.auth import get_user_model

from apps.api.tests.factories import UserFactory


@pytest.mark.integration
@pytest.mark.django_db
def test_user_is_stored_in_postgres():
    created = UserFactory(username="ada")

    stored = get_user_model().objects.get(username="ada")

    assert stored.pk == created.pk
    assert stored.email == "ada@example.com"
    assert stored.check_password("password")
