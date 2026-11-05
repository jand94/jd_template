# API

Öffentliche Endpunkte setzen `permission_classes` ausdrücklich auf `AllowAny`. Alles andere verlangt eine Sitzung. Das gilt über `DEFAULT_PERMISSION_CLASSES`.

Listen aus `GenericAPIView` antworten mit `PagePagination`:

```json
{"count": 0, "next": null, "previous": null, "results": []}
```

Die Seite steht in `page`, die Größe in `page_size`, höchstens 100, Standard 20.

Fehler, die der Client als `ApiError` liest:

- `detail` ist ein String.
- Jedes weitere Feld ist eine Liste von Strings.
- Unbehandelte Ausnahmen antworten mit Status 500 und `{"detail": "Die Anfrage ist fehlgeschlagen."}`. Der Log enthält die Ursache, der Körper nicht.

Schema und Swagger bleiben ohne Sitzung erreichbar.

Die Registrierung startet eine Sitzung und schickt einen Bestätigungslink an die E-Mail. `POST /accounts/v1/email/verify/` setzt `email_verified_at`. Der Körper enthält `uid` und `token` aus dem Link `{FRONTEND_ORIGIN}/email-bestaetigen`. Ein angemeldetes Konto fordert denselben Link mit `POST /accounts/v1/email/verify/send/` erneut an, solange die Adresse offen ist. Eine geänderte E-Mail löscht die Bestätigung und verschickt einen neuen Link.

`POST /accounts/v1/password/reset/` antwortet immer gleich. Die Mail enthält `{FRONTEND_ORIGIN}/passwort-setzen` mit `uid` und `token`. `POST /accounts/v1/password/reset/confirm/` setzt das Passwort.
