from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = "apps.common"
    label = "common"
    verbose_name = "Common"

    def ready(self):
        # Registriert die OpenAPI-Erweiterung beim Import.
        import apps.common.api.v1.schema.common  # noqa: F401
        from apps.common.services.audit import connect_auth_signals, connect_model_auditing

        connect_auth_signals()
        connect_model_auditing()
