from rest_framework.authentication import SessionAuthentication


class AccountSessionAuthentication(SessionAuthentication):
    """Sitzungsauthentifizierung, die bei fehlender Anmeldung 401 statt 403 liefert."""

    def authenticate_header(self, request):
        return "Session"
