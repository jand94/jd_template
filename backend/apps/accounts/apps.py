from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "apps.accounts"
    label = "accounts"

    def ready(self):
        # Registriert die OpenAPI-Erweiterung beim Import.
        import apps.accounts.api.v1.schema.accounts  # noqa: F401
