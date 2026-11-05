from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = "apps.common"
    label = "common"
    verbose_name = "Common"

    def ready(self):
        from apps.common.services.audit import connect_auth_signals, connect_model_auditing

        connect_auth_signals()
        connect_model_auditing()
