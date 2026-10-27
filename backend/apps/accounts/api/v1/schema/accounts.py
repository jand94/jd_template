from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import extend_schema

ACCOUNTS_TAG = "Accounts"


class AccountSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.accounts.api.v1.authentication.AccountSessionAuthentication"
    name = "sessionAuth"
    priority = -1

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": settings.SESSION_COOKIE_NAME,
            "description": (
                "Django session cookie. Unsafe requests from a browser also send "
                "the CSRF token in the X-CSRFToken header."
            ),
        }


def accounts_schema(**kwargs):
    kwargs.setdefault("tags", [ACCOUNTS_TAG])
    return extend_schema(**kwargs)
