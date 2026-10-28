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
