import re

import pytest
from django.core.exceptions import ValidationError
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from apps.accounts.models.validators import validate_iso_country

TWO_LETTERS = re.compile(r"^[A-Za-z]{2}$")


@pytest.mark.unit
@hypothesis_settings(max_examples=40, deadline=None)
@given(st.from_regex(r"^[A-Za-z]{2}$", fullmatch=True))
def test_iso_country_accepts_two_letters(value):
    validate_iso_country(value)


@pytest.mark.unit
@hypothesis_settings(max_examples=40, deadline=None)
@given(st.text(min_size=1, max_size=8).filter(lambda value: TWO_LETTERS.fullmatch(value) is None))
def test_iso_country_rejects_anything_else(value):
    with pytest.raises(ValidationError):
        validate_iso_country(value)
