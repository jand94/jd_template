# Betrieb

Der Dev-Stack bleibt `make dev`. Auslieferung nutzt dieselben Images mit dem Ziel `prod`.

## Umgebung

`DEBUG`, `SECRET_KEY`, Mail und die Cookie-Flags kommen aus der Umgebung. `docker/.env.example` ist der lokale Stand. `docker/.env.prod.example` ist die Vorlage für `docker/.env.prod`.

`EMAIL_BACKEND` wählt die Klasse von `MAILERS["default"]`. Für SMTP kommen Host, Port, Benutzer und TLS aus `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` und `EMAIL_USE_TLS`. Das Django-Setting `EMAIL_BACKEND` bleibt ungesetzt.

`REDIS_PASSWORD` schützt Redis. Django hängt das Passwort an die Cache-URL. `FRONTEND_ORIGIN` ist die Browser-Adresse in Links für Passwort und E-Mail-Bestätigung, zum Beispiel `https://example.com`.

`ALLOWED_HOSTS` nennt den öffentlichen Host. `localhost`, `127.0.0.1` und `backend` bleiben zusätzlich erlaubt, weil der Healthcheck und der Next-Proxy Django unter diesen Namen erreichen.

Sobald `DEBUG` aus ist, verlangt Django einen `SECRET_KEY`. Session- und CSRF-Cookies werden dann nur über HTTPS gesendet, HTTP wird auf HTTPS umgeleitet, und HSTS ist an. Der TLS-Abschluss muss `X-Forwarded-Proto` setzen und einen vom Client gelieferten Wert verwerfen. `SECURE_PROXY_SSL_HEADER` erwartet genau diesen Header.

`CSRF_COOKIE_HTTPONLY` bleibt aus, weil der Browser-Client das Cookie selbst liest. `SameSite` ist `Lax`.

## Prozess

`docker/compose.prod.yml` baut die Stufe `prod`.

```bash
cp docker/.env.prod.example docker/.env.prod
make prod
```

Das Backend startet Gunicorn mit `backend/gunicorn.conf.py`. Das Access-Log enthält die `X-Request-ID` der Antwort. Static-Dateien sammelt das Image mit `collectstatic` und liefert sie über WhiteNoise aus. `SERVE_MEDIA=true` lässt denselben Prozess hochgeladene Dateien ausliefern. Ein späterer Speicher tritt an die Stelle von `STORAGES["default"]`, ohne die Views zu ändern.

Die Stufe `prod` läuft ohne root. Das Backend nutzt den Benutzer `app`, das Frontend den Benutzer `node` aus dem Node-Image. Beide haben UID 1000. `media` und `staticfiles` gehören `app`. Die Dev-Stufe bleibt root, weil die Bind-Mounts dem Host gehören.

Das Frontend-Image führt `next build` aus, installiert die Laufzeit ohne Dev-Pakete und startet `next start`. Antworten tragen `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy` und eine Content-Security-Policy. Skripte und Styles erlauben `'unsafe-inline'`, weil das Theme beim Laden ein Inline-Skript braucht und Tailwind Inline-Styles setzt.

`docker/compose.prod.yml` veröffentlicht das Backend nicht. Der Dienst `proxy` bindet `FRONTEND_PORT` als HTTPS und setzt `X-Forwarded-Proto: https`. API und Admin laufen über das Frontend oder `docker compose exec`. Redis und PostgreSQL bleiben im Compose-Netz.

`PROD_TLS_MODE=generate` erzeugt vor `make prod` eine eigene Root-CA und ein Serverzertifikat unter `docker/certs/prod/`. Die Namen sind dieselben wie in der Entwicklung, dazu die kommagetrennte Liste `PROD_CERT_DNS`. Clients importieren `docker/certs/prod/prod-ca.crt`. `PROD_TLS_MODE=own` kopiert `PROD_TLS_CERT` und `PROD_TLS_KEY` an den Proxy. Die Dev-CA gilt für diesen Stapel nicht. Dateien, Import und die beiden Modi stehen in [docs/tutorials/04-zertifikate.md](../tutorials/04-zertifikate.md).

## Prüfungen

```bash
make check-deploy
make check-migrations
```

`make check-deploy` setzt `DEBUG=false`, einen eigenen Schlüssel und den SMTP-Mailer und lässt `manage.py check --deploy` an Warnungen scheitern. Der lokale Stack mit `DEBUG=true` und der Konsole bleibt davon unberührt.

## Bereitschaft

`GET /api/v1/health/` ist das Lebenszeichen und prüft keine Abhängigkeit. `GET /api/v1/ready/` prüft PostgreSQL und Redis und antwortet `503`, wenn eine Prüfung fehlschlägt. Die Körper enthalten `ok` oder `error`, keine Verbindungsdetails. Compose nutzt `ready` als Healthcheck und sendet `X-Forwarded-Proto: https`, damit der Redirect den Check nicht umleitet.

Jede Antwort trägt `X-Request-ID`. Ein sicherer Wert aus dem Request wird übernommen, sonst vergibt Django einen neuen. Logzeilen enthalten dieselbe Kennung.
