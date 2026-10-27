import pytest

from apps.accounts.admin import AccountUserAdmin
from apps.accounts.admin.filters import EmailVerifiedFilter, PhoneVerifiedFilter
from apps.accounts.admin.forms import AccountUserChangeForm, AccountUserCreationForm
from apps.accounts.models import User


def _field_names():
    names = []
    for _label, options in AccountUserAdmin.fieldsets:
        for field in options["fields"]:
            if isinstance(field, tuple):
                names.extend(field)
            else:
                names.append(field)
    return names


@pytest.mark.unit
def test_admin_forms_use_the_project_user():
    assert AccountUserChangeForm._meta.model is User
    assert AccountUserCreationForm._meta.model is User
    assert AccountUserCreationForm._meta.fields == ("username", "email")
    assert AccountUserAdmin.form is AccountUserChangeForm
    assert AccountUserAdmin.add_form is AccountUserCreationForm


@pytest.mark.unit
def test_admin_change_form_covers_profile_address_and_computed_fields():
    fields = set(_field_names())

    assert {
        "street",
        "city",
        "date_of_birth",
        "phone",
        "language",
        "age",
        "formatted_address",
        "is_email_verified",
        "groups",
    } <= fields
    assert set(AccountUserAdmin.readonly_fields) <= fields
    assert "email" in AccountUserAdmin.add_fieldsets[0][1]["fields"]


@pytest.mark.unit
def test_admin_registers_bulk_actions_and_verification_filters():
    assert {
        "activate_users",
        "deactivate_users",
        "mark_email_verified",
        "mark_phone_verified",
    } <= set(AccountUserAdmin.actions)
    assert EmailVerifiedFilter in AccountUserAdmin.list_filter
    assert PhoneVerifiedFilter in AccountUserAdmin.list_filter
    assert [value for value, _label in EmailVerifiedFilter.lookups(None, None, None)] == [
        "yes",
        "no",
    ]
