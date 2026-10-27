from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'
    label = 'accounts'

    def ready(self):
        from apps.accounts.api.v1.schema import accounts as _accounts_schema

        _accounts_schema
