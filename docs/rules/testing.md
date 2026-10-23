# Testing

Tests prüfen Verhalten über die vier Schichten Unit, Integration, API und Last. Sie liegen in der App, die das Verhalten besitzt.

```text
backend/apps/<app>/tests/
  factories.py
  unit/
  integration/
  api/
```

Gemeinsame Fixtures, darunter `api_client`, stehen in `backend/conftest.py`.

## Werkzeuge

| Werkzeug | Aufgabe |
|---|---|
| pytest | Testframework |
| pytest-django | Django-Setup und Testdatenbank |
| pytest-cov | Abdeckung von `apps` |
| DRF `APIClient` | HTTP-Endpunkte |
| factory_boy | Testdaten, Django-Modelle über `DjangoModelFactory` |
| pytest-mock | Externe Dienste |
| freezegun | Zeitabhängige Logik |
| Locust | Last und Durchsatz |

Hypothesis ist für Property-based Tests vorgesehen und noch nicht eingebunden. Die Pakete stehen in `backend/requirements-dev.txt`.

## Testarten

**Unit** (`@pytest.mark.unit`): eine Funktion oder Geschäftsregel. Keine Datenbank, kein HTTP, keine externen Dienste. Serializer-Validierung und reine Services gehören hierher.

**Integration** (`@pytest.mark.integration` und `@pytest.mark.django_db`): Zusammenspiel von Django, PostgreSQL, Berechtigungen und Services. Freigaben, Revisionen und Persistenz gehören hierher. Testdaten kommen aus Factories.

**API** (`@pytest.mark.api` und `@pytest.mark.django_db`): ein HTTP-Endpunkt über `api_client`. Der Test prüft Authentifizierung, Validierung, Statuscode, Antwortformat und Objektberechtigungen. URLs werden mit `reverse` aufgelöst.

**Last** (`backend/locustfile.py`): viele gleichzeitige Benutzer gegen den laufenden Stack. Gemessen werden Antwortzeit, Fehlerrate und Durchsatz. Lasttests laufen nicht in pytest.

## Regeln

- Ein Test hat einen Grund zu scheitern. Setup liegt in Fixtures und Factories.
- Unit-Tests fragen die Datenbank nicht an. Integration und API markieren `django_db`, damit pytest-django eine eigene Testdatenbank benutzt.
- Externe Systeme werden mit `pytest-mock` ersetzt. Zeit wird mit freezegun festgehalten, wenn das Ergebnis vom aktuellen Zeitpunkt abhängt.
- Neue öffentliche Funktionen bekommen den passenden Test in `unit`, `integration` oder `api`.
- Abdeckung bezieht sich auf `apps` und lässt `migrations` und `tests` aus.

## Befehle

Der Dev-Stack läuft, damit pytest die Testdatenbank in PostgreSQL anlegen kann.

```bash
make test
make test-unit
make test-integration
make test-api
make loadtest
```

`make loadtest` startet Locust headless mit 100 Benutzern für 30 Sekunden. `LOCUST_USERS`, `LOCUST_SPAWN_RATE` und `LOCUST_RUN_TIME` ändern den Lauf.
