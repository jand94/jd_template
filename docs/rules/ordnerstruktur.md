# Ordnerstruktur

## Repository

```text
jd_pmgt/
  backend/                 Django-Projekt
    backend/               Grundkonfiguration (settings, urls, wsgi, asgi)
    apps/<app>/            Fach-Apps
    conftest.py            gemeinsame pytest-Fixtures
    locustfile.py          Lasttests
    manage.py
    pytest.ini
    requirements.txt
    requirements-dev.txt
  frontend/                Next.js
  docker/
    .env                   Host-Ports und Datenbankzugang
    compose.yml
    backend/Dockerfile
    frontend/Dockerfile
  docs/rules/
  scripts/create_app.py
  Makefile
```

`backend/backend` ist die Projektkonfiguration. Fachlichkeit liegt nicht dort, sondern in `backend/apps/<app>`.

## App

Jede App hat diese Form. `make create_app <appname>` legt sie an, trägt sie unter `interne Apps` in `INSTALLED_APPS` ein und hängt `path("<app>/", include("apps.<app>.urls"))` in `backend/backend/urls.py` ein.

```text
backend/apps/<app>/
  admin/
  api/
    v1/
      permissions/
      schema/
      serializers/
      services/
      views/
      urls.py
  exceptions/
  migrations/
  models/
  services/
  tests/
    unit/
    integration/
    api/
  apps.py
  urls.py
```

Der App-Name beginnt mit einem Kleinbuchstaben und enthält nur Kleinbuchstaben, Ziffern und Unterstriche. Reserviert sind `apps`, `backend`, `config`, `django`, `test` und `tests`.

## Pakete

Ordner sind Python-Pakete. Öffentliche Modelle, Serializer, Views und Factories werden im `__init__.py` des Pakets importiert. Django registriert Modelle nur, wenn `models/__init__.py` sie importiert.

`apps.py` liegt am App-Root. `AppConfig.name` ist `apps.<app>`, `label` ist der kurze App-Name. In `INSTALLED_APPS` steht der Pfad `apps.<app>.apps.<App>Config` im Abschnitt `interne Apps`. Django-Beiträge und Drittanbieter bleiben in ihren eigenen Abschnitten.

## API-Versionen

`apps/<app>/urls.py` bindet die aktuelle Version ein:

```python
path("v1/", include("apps.<app>.api.v1.urls"))
```

Die HTTP-Basis einer App ist `/<app>/v1/`. Eine neue Version ist ein Geschwisterpaket von `v1` und bekommt in der App-`urls.py` einen eigenen `path`. Routen einer Version stehen in `api/<version>/urls.py`.

`permissions`, `schema`, `serializers`, `services` und `views` gehören zur Version. Domänenlogik, die keine HTTP-Schicht ist, liegt in `apps/<app>/services` und `apps/<app>/models`.
