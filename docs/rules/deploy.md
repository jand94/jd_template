# Betrieb

Der Dev-Stack bleibt `make dev`. Auslieferung nutzt dieselben Images mit dem Ziel `prod`.

## Umgebung

`DEBUG`, `SECRET_KEY`, Mail und die Cookie-Flags kommen aus der Umgebung. `docker/.env.example` ist der lokale Stand. `docker/.env.prod.example` ist die Vorlage für `docker/.env.prod`.

`EMAIL_BACKEND` wählt die Klasse von `MAILERS["default"]`. Für SMTP kommen Host, Port, Benutzer und TLS aus `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` und `EMAIL_USE_TLS`. Das Django-Setting `EMAIL_BACKEND` bleibt ungesetzt.

Sobald `DEBUG` aus ist, verlangt Django einen `SECRET_KEY`. Session- und CSRF-Cookies werden dann nur über HTTPS gesendet, HTTP wird auf HTTPS umgeleitet, und HSTS ist an. Der TLS-Abschluss muss `X-Forwarded-Proto` setzen und einen vom Client gelieferten Wert verwerfen. `SECURE_PROXY_SSL_HEADER` erwartet genau diesen Header.

`CSRF_COOKIE_HTTPONLY` bleibt aus, weil der Browser-Client das Cookie selbst liest. `SameSite` ist `Lax`.

## Prozess

`docker/compose.prod.yml` baut die Stufe `prod`.

```bash
cp docker/.env.prod.example docker/.env.prod
make prod
```

Das Backend startet Gunicorn. Static-Dateien sammelt das Image mit `collectstatic` und liefert sie über WhiteNoise aus. `SERVE_MEDIA=true` lässt denselben Prozess hochgeladene Dateien ausliefern. Ein späterer Speicher tritt an die Stelle von `STORAGES["default"]`, ohne die Views zu ändern.

Das Frontend-Image führt `next build` aus und startet `next start`.

## Prüfungen

```bash
make check-deploy
make check-migrations
```

`make check-deploy` setzt `DEBUG=false`, einen eigenen Schlüssel und den SMTP-Mailer und lässt `manage.py check --deploy` an Warnungen scheitern. Der lokale Stack mit `DEBUG=true` und der Konsole bleibt davon unberührt.

## Bereitschaft

`GET /api/v1/health/` ist das Lebenszeichen und prüft keine Abhängigkeit. `GET /api/v1/ready/` prüft PostgreSQL und Redis und antwortet `503`, wenn eine Prüfung fehlschlägt. Die Körper enthalten `ok` oder `error`, keine Verbindungsdetails. Compose nutzt `ready` als Healthcheck und sendet `X-Forwarded-Proto: https`, damit der Redirect den Check nicht umleitet.

Jede Antwort trägt `X-Request-ID`. Ein sicherer Wert aus dem Request wird übernommen, sonst vergibt Django einen neuen. Logzeilen enthalten dieselbe Kennung.
