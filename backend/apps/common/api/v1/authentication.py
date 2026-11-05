from rest_framework.authentication import SessionAuthentication


class CommonSessionAuthentication(SessionAuthentication):
    """Sitzung für die lesende Audit-API. Ungültige Sitzungen antworten mit 401."""

    def authenticate_header(self, request):
        return "Session"
