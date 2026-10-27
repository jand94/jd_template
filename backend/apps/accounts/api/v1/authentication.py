from rest_framework.authentication import SessionAuthentication


class AccountSessionAuthentication(SessionAuthentication):
    """Sitzungsauthentifizierung mit CSRF für anonyme und angemeldete Requests.

    DRF prüft CSRF in der Basisklasse nur, wenn bereits ein aktiver Benutzer in
    der Session steckt. Hier wird die Prüfung vor dem Benutzer-Check ausgeführt,
    damit Login, Registrierung und Passwort-Reset nicht ohne Token möglich sind.
    """

    def authenticate(self, request):
        self.enforce_csrf(request)

        user = getattr(request._request, "user", None)
        if not user or not user.is_active:
            return None
        return (user, None)

    def authenticate_header(self, request):
        return "Session"
