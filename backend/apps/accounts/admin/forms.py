from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm, UsernameField

from apps.accounts.models import User


class AccountUserCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        field_classes = {"username": UsernameField}


class AccountUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
