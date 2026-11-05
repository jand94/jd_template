# Umgebung, weitere Datenbanken, Make

Dieses Kapitel erklärt, welche Datei welchen Prozess konfiguriert, wie eine Datenbank eines Drittsystems dazukommt, und was jedes Make-Ziel tut. Der erste Start selbst steht in [Kapitel 1](01-ubuntu-vm.md).

Es gibt zwei Umgebungsdateien. Beide sind Kopien einer Vorlage und stehen in `.gitignore`.

| Datei | Vorlage | Compose-Datei | Start |
|---|---|---|---|
| `docker/.env` | `docker/.env.example` | `docker/compose.yml` | `make dev` |
| `docker/.env.prod` | `docker/.env.prod.example` | `docker/compose.prod.yml` | `make prod` |

`make` übergibt die Datei mit `--env-file`. Compose ersetzt damit `${POSTGRES_DB}` und die übrigen Platzhalter in der Compose-Datei. Zusätzlich lädt der Backend-Dienst dieselbe Datei als `env_file` in den Container. Das Frontend lädt sie nicht. Es bekommt nur die Variablen, die im Dienst `environment` ausdrücklich nennt.

## Vorrang

Drei Schichten, die später gewinnt:

1. Der Default in `backend/backend/settings.py`, wenn die Variable im Prozess fehlt.
2. `env_file`, also jede Zeile aus `docker/.env` bzw. `docker/.env.prod`.
3. Der Block `environment` des Dienstes in der Compose-Datei. Er überschreibt `env_file` für diesen Container.

Für das Backend setzt der Dev-Compose-Block fest:

```yaml
POSTGRES_HOST: db
POSTGRES_PORT: "5432"
REDIS_HOST: redis
REDIS_PORT: "6379"
FRONTEND_ORIGIN: https://127.0.0.1:${FRONTEND_PORT}
ALLOWED_HOSTS: localhost,127.0.0.1,backend
CSRF_TRUSTED_ORIGINS: https://127.0.0.1:${FRONTEND_PORT},https://localhost:${FRONTEND_PORT},https://127.0.0.1:${BACKEND_PORT},https://localhost:${BACKEND_PORT}
SESSION_COOKIE_SECURE: "true"
CSRF_COOKIE_SECURE: "true"
```

Dieselben Host- und Port-Zeilen stehen in `docker/compose.prod.yml`. `FRONTEND_ORIGIN` kommt in der Produktion aus `docker/.env.prod`, weil der Prod-Block `${FRONTEND_ORIGIN}` einsetzt. `ALLOWED_HOSTS` und `CSRF_TRUSTED_ORIGINS` setzt der Prod-Block nicht. Dort gelten die Zeilen aus `docker/.env.prod`.

Folge für den Alltag: `POSTGRES_PORT=5433` in `docker/.env` veröffentlicht PostgreSQL auf der VM unter Port 5433. Django verbindet sich weiter mit `db:5432`. Wer die Anwendungsdatenbank auf einen anderen Rechner legen will, ändert den Compose-Block `POSTGRES_HOST` und `POSTGRES_PORT`. Ein zweiter Eintrag in `docker/.env` allein reicht nicht, weil Compose ihn überschreibt.

`make urls` liest `docker/.env` mit `set -a && . docker/.env`. Eine Zeile ohne Anführungszeichen wird dabei von der Shell zerschnitten, sobald sie ein Leerzeichen enthält. Werte mit Leerzeichen stehen in doppelten Anführungszeichen:

```bash
API_DESCRIPTION="HTTP-API für das Projekt"
```

Kommentare beginnen mit `#`. Leere Zeilen sind erlaubt. Die Datei enthält keine Export-Anweisung.

Nach einer Änderung an `docker/.env`:

| Geändert | Wirkt nach |
|---|---|
| Host-Port | `make down` und `make dev`, weil die Veröffentlichung am Container hängt |
| Passwort, `SECRET_KEY`, Mail, Marke, Superuser | `make restart backend` |
| `PROJECT_NAME`, `API_TITLE`, `API_DESCRIPTION`, `API_VERSION` | `make restart frontend` in der Entwicklung. In der Produktion zusätzlich `make prod`, weil das Frontend-Image die vier Werte beim Build einbrennt |
| `POSTGRES_PASSWORD` bei schon initialisiertem Volume | kein Neustart. PostgreSQL liest das Passwort nur beim ersten Anlegen des Volumes. Bestehende Datenbank: Passwort in `psql` ändern, oder Volume verwerfen |

`make restart dev` startet alle vier Dienste neu.

## Variablen der Entwicklung

Vorlage: `docker/.env.example`.

### Türen auf der VM

| Variable | Vorlage | Bedeutung |
|---|---|---|
| `BACKEND_PORT` | `8000` | Host-Port für Django, HTTPS über den Proxy. Swagger, Admin, Health und Ready |
| `FRONTEND_PORT` | `3000` | Host-Port für Next.js, HTTPS über den Proxy |
| `POSTGRES_PORT` | `5432` | Host-Port für PostgreSQL. Im Backend-Container immer `5432` |
| `REDIS_PORT` | `6379` | Host-Port für Redis. Im Backend-Container immer `6379` |

Ein Client auf der VM, der an PostgreSQL vorbeigehen will, nutzt `127.0.0.1` und `POSTGRES_PORT`. `make psql` geht den anderen Weg und öffnet `psql` im Container `db`. Dort ist der Port `5432`, und das Passwort kennt der Container über seine eigene Umgebung.

### Anwendungsdatenbank und Cache

| Variable | Vorlage | Gelesen von |
|---|---|---|
| `POSTGRES_DB` | `jd_template` | PostgreSQL beim ersten Volume, Django `DATABASES["default"]["NAME"]`, Healthcheck |
| `POSTGRES_USER` | `jd_template` | wie `POSTGRES_DB`, für den Benutzer |
| `POSTGRES_PASSWORD` | `jd_template` | wie `POSTGRES_DB`, für das Passwort |
| `REDIS_PASSWORD` | `jd_template` | `redis-server --requirepass`, Django-Cache, `REDISCLI_AUTH` |

Die Anwendungsdatenbank ist der Alias `default` in `DATABASES`. Engine ist `django.db.backends.postgresql`. Sessions liegen in PostgreSQL und zusätzlich im Redis-Cache (`SESSION_ENGINE = cached_db`). Redis ist kein zweiter Datenbestand. Ein leerer Redis verliert nur den Cache. Die Sitzungen bleiben in PostgreSQL lesbar und werden beim nächsten Zugriff nachgeladen.

`make redis-cli` öffnet `redis-cli` im Container. Die Authentifizierung übernimmt `REDISCLI_AUTH`.

### Django

| Variable | Vorlage | Wirkung |
|---|---|---|
| `DEBUG` | `true` | Debug-Seiten, HTTP-Cookies, keine HTTPS-Umleitung, kein erzwungener `SECRET_KEY` |
| `SECRET_KEY` | ein lokaler Platzhalter | Signatur von Sessions, CSRF und Tokens. Ab `DEBUG=false` verweigert Django den Start, wenn der Wert leer ist |
| `EMAIL_BACKEND` | Konsole | Klasse von `MAILERS["default"]`. Das Django-Setting `EMAIL_BACKEND` bleibt ungesetzt, Django 6 liest `MAILERS` |
| `SERVE_MEDIA` | `true` | Django liefert `/media/` selbst aus. In der Produktion entscheidet dieselbe Variable, ob der Prozess das übernimmt |

Die Konsole schreibt Mails ins Backend-Log (`make logs backend`). Tests ersetzen den Mailer in `backend/conftest.py` durch den Speicher-Mailer, unabhängig von dieser Variable.

SMTP steht in der Produktionsvorlage: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`. Die Settings bauen daraus die Optionen, sobald der Backend-Pfad auf `smtp.EmailBackend` endet. Port 587 gilt bei TLS, sonst 25. Ein leerer Benutzer wird zu `None`.

`DEFAULT_FROM_EMAIL` ist der Absender. Die Vorlage setzt `jd_template@localhost`.

`LOG_LEVEL` hat keine Zeile in der Vorlage. Fehlt sie, loggt der Root-Logger auf `INFO`.

### Namen

| Variable | Vorlage | Verwendung |
|---|---|---|
| `PROJECT_NAME` | `jd_template` | Oberfläche, Admin-Titel, Fallback für API-Titel und Absender |
| `API_TITLE` | `jd_template API` | OpenAPI und Swagger |
| `API_DESCRIPTION` | `HTTP-API für jd_template` | OpenAPI |
| `API_VERSION` | `0.1.0` | OpenAPI |

Das Frontend liest dieselben vier Namen in `frontend/src/config/brand.ts`. Compose übergibt sie an den Frontend-Container. Der Browser sieht sie nach `make restart frontend`.

### Erster Superuser

| Variable | Vorlage |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` |
| `DJANGO_SUPERUSER_PASSWORD` | `jd_template` |

`ensure_superuser` läuft bei jedem Start des Dev-Backends und beim Prod-Start, legt den Benutzer aber nur an, wenn der Name fehlt. Ein geändertes Passwort in der Umgebung ändert den bestehenden Benutzer nicht. Dafür `make createsuperuser` oder das Admin.

## Variablen, die nur der Compose-Block setzt

Diese Namen können in `docker/.env` stehen und werden im Backend trotzdem vom Compose-Block ersetzt. Die Tabelle nennt den Wert, der im Container gilt.

| Variable | Dev-Container | Prod-Container |
|---|---|---|
| `POSTGRES_HOST` | `db` | `db` |
| `POSTGRES_PORT` | `5432` | `5432` |
| `REDIS_HOST` | `redis` | `redis` |
| `REDIS_PORT` | `6379` | `6379` |
| `FRONTEND_ORIGIN` | `https://127.0.0.1:<FRONTEND_PORT>` | Wert aus `docker/.env.prod` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,backend` | Wert aus `docker/.env.prod` |
| `CSRF_TRUSTED_ORIGINS` | `https` für Frontend- und Backend-Port, jeweils `127.0.0.1` und `localhost` | Wert aus `docker/.env.prod` |
| `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | `true` | Default aus `DEBUG`: an, sobald `DEBUG` aus ist |
| `API_ORIGIN` | `http://backend:8000`, nur im Frontend | derselbe Wert |
| `DEBUG` | aus `docker/.env` | der Prod-Block setzt `false` |

`API_ORIGIN` ist die Adresse, unter der Next.js Django im Compose-Netz ruft. Der Browser verwendet sie nicht. Der Browser ruft denselben Ursprung wie die Seite, und die Route-Handler unter `frontend/src/app/accounts` und `frontend/src/app/media` leiten an `API_ORIGIN` weiter.

`FRONTEND_ORIGIN` baut Links in Mails: `{FRONTEND_ORIGIN}/email-bestaetigen` und `{FRONTEND_ORIGIN}/passwort-setzen`. In der Entwicklung zeigt der Wert auf `https://127.0.0.1` und den Frontend-Port. Wer das Frontend über einen SSH-Tunnel auf dem Laptop öffnet, bleibt bei dieser Adresse, weil der Tunnel genau dort endet. Das Zertifikat und der Import stehen in [Kapitel 1](01-ubuntu-vm.md).

Weitere Namen aus `settings.py`, ohne Zeile in der Vorlage:

| Variable | Default, wenn sie fehlt |
|---|---|
| `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` | an, sobald `DEBUG` aus ist |
| `SECURE_HSTS_SECONDS` | `31536000`, sobald `DEBUG` aus ist, sonst `0` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,backend` |

`CSRF_COOKIE_HTTPONLY` bleibt aus. Der Browser-Client liest `csrftoken` aus `document.cookie` und sendet ihn als `X-CSRFToken`. `SameSite` ist `Lax`.

## Produktion, kurz auf die Unterschiede

`docker/.env.prod.example` wiederholt Datenbank, Redis, Marke und Superuser und ergänzt den öffentlichen Betrieb:

- `DEBUG=false`
- `SECRET_KEY` als Platzhalter, der vor dem Start ersetzt wird
- SMTP statt Konsole
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_ORIGIN` auf den öffentlichen Namen
- kein `BACKEND_PORT`, kein `POSTGRES_PORT`, kein `REDIS_PORT`, weil `compose.prod.yml` diese drei Dienste nicht veröffentlicht
- `FRONTEND_PORT` bleibt, weil das Frontend der einzige veröffentlichte Dienst ist

Der TLS-Abschluss und der Header `X-Forwarded-Proto` stehen in [Kapitel 1](01-ubuntu-vm.md). Cookies, HSTS und die Bereitschaft beschreibt [docs/rules/deploy.md](../rules/deploy.md).

## Eine weitere Datenbank

Die Vorlage kennt einen Alias: `default`, die PostgreSQL-Instanz im Compose-Netz. Eine Datenbank eines Drittsystems — ein ERP, ein Warenwirtschaftssystem, ein Berichtsserver — wird ein weiterer Alias in `DATABASES`. Sie bekommt eigene Variablen. `POSTGRES_HOST` und `POSTGRES_PORT` bleiben der Compose-Datenbank vorbehalten, weil der Compose-Block sie auf `db` und `5432` festsetzt.

Beispiel: ein PostgreSQL-Server `erp.internal`, nur lesend, Bestandstabelle `customers`. Der Alias heißt `erp`.

### Variablen

In `docker/.env` und, sobald der Server sie auch in der Produktion braucht, in `docker/.env.prod`:

```bash
ERP_DB_NAME=erp
ERP_DB_USER=jd_template_read
ERP_DB_PASSWORD=ein-langes-passwort
ERP_DB_HOST=erp.internal
ERP_DB_PORT=5432
ERP_DB_SSLMODE=require
```

`env_file` reicht jede Zeile an den Backend-Container weiter. Die Namen kollidieren mit keinem Compose-Block, deshalb kommen sie unverändert in `os.environ` an. Das Frontend sieht sie nicht und braucht sie nicht.

Das Passwort liegt nur in den beiden gitignorierten Dateien. Die Vorlagen `docker/.env.example` und `docker/.env.prod.example` bekommen höchstens die Schlüsselnamen mit leerem Wert, wenn das Team denselben Satz Variablen teilen soll.

Auf dem Drittsystem einen eigenen Benutzer anlegen, der genau die Tabellen lesen darf, die das Modul abfragt. Die Anwendungsdatenbank `default` und dieser Benutzer bleiben getrennte Konten.

### Erreichbarkeit aus dem Container

Der Backend-Container löst Hostnamen über das Netz der VM auf. Ausgehend erlaubt UFW den Verkehr. Die Firewall des Drittsystems muss die Adresse der VM auf dem Datenbankport zulassen.

Drei Lagen, drei Adressen:

| Lage der Datenbank | `ERP_DB_HOST` |
|---|---|
| Anderer Rechner | DNS-Name oder IP, zum Beispiel `erp.internal` |
| Weiterer Compose-Dienst in derselben Datei | Dienstname, zum Beispiel `erp` |
| PostgreSQL, das auf der VM selbst läuft und nicht der Compose-Dienst `db` ist | `host.docker.internal` |

`127.0.0.1` im Container ist der Container, nicht die VM. Für eine Datenbank auf der VM selbst den Backend-Dienst in `docker/compose.yml` und `docker/compose.prod.yml` ergänzen:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Der Datenbankserver auf der VM muss dann an der Docker-Bridge lauschen, nicht nur an `127.0.0.1`. Sonst erreicht der Container ihn trotz des Namens nicht.

### Settings

In `backend/backend/settings.py` den Alias neben `default` eintragen. Fehlt eine Pflichtvariable, startet der Prozess nicht. Ein stiller Fallback auf `localhost` würde Anfragen an die falsche Datenbank schicken.

```python
def require_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} fehlt.")
    return value


DATABASES["erp"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": require_env("ERP_DB_NAME"),
    "USER": require_env("ERP_DB_USER"),
    "PASSWORD": require_env("ERP_DB_PASSWORD"),
    "HOST": require_env("ERP_DB_HOST"),
    "PORT": require_env("ERP_DB_PORT"),
    "OPTIONS": {
        "sslmode": os.environ.get("ERP_DB_SSLMODE", "require"),
        "connect_timeout": 5,
    },
    "CONN_MAX_AGE": 60,
    "AUTOCOMMIT": True,
}
```

`CONN_MAX_AGE` hält die Verbindung über mehrere Anfragen. `connect_timeout` verhindert, dass ein unerreichbares Drittsystem einen Gunicorn-Worker minutenlang blockiert.

Wer den Alias nur in manchen Installationen braucht, liest `ERP_DB_HOST` und trägt `DATABASES["erp"]` nur ein, wenn der Wert gesetzt ist. Der Router weiter unten darf den Alias dann nur verwenden, wenn er in `DATABASES` steht.

Andere Engines folgen demselben Muster. Eine SQL-Server- oder MySQL-Datenbank braucht den passenden Django-Backend-Namen und das Paket in `backend/requirements.txt`, danach `make build backend` und `make install-backend`. Die PostgreSQL-Engine der Vorlage deckt den Compose-Dienst und jeden weiteren PostgreSQL-Server ab.

### Router

Django wandert mit `migrate` über jeden Alias, für den ein Router die Migration erlaubt. Auf einem Drittsystem darf dieser Lauf keine Tabelle anlegen und keine ändern. Ein Router in `backend/backend/db_routers.py` verbietet das und schickt genau eine App an den Alias `erp`.

Die App entsteht mit `make create_app erp`, wie jede andere App in [Kapitel 3](03-eigene-implementierung.md). Ihre Modelle beschreiben vorhandene Tabellen und tragen `managed = False`.

```python
class ErpRouter:
    app_label = "erp"
    alias = "erp"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.alias
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.alias
        return None

    def allow_relation(self, obj1, obj2, **hints):
        labels = {obj1._meta.app_label, obj2._meta.app_label}
        if self.app_label in labels and labels != {self.app_label}:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == self.alias:
            return False
        if app_label == self.app_label:
            return False
        return None
```

`db_for_read` und `db_for_write` schicken die App `erp` an denselben Alias. Der Benutzer auf dem Drittsystem darf nur lesen. Ein `save()` trifft damit `erp` und scheitert an den Rechten der Datenbank, statt eine Tabelle in `default` anzulegen. `allow_migrate` lässt denselben Alias bei `migrate` aus. Schreibrechte auf dem Drittsystem gibt es erst, wenn ein Modul den Bestand ändern soll und der Benutzer dort genau diese Rechte bekommt.

In `settings.py`:

```python
DATABASE_ROUTERS = ["backend.db_routers.ErpRouter"]
```

Fremde Tabellen bekommen keinen ForeignKey auf `accounts.User` oder ein anderes Modell in `default`. Django erlaubt Beziehungen über Alias-Grenzen nicht, sobald der Router sie ablehnt. Die fachliche Verknüpfung speichert den fremden Schlüssel als Integer oder Zeichenkette im eigenen Modell.

Modell, passend zu einer vorhandenen Tabelle `customers` mit den Spalten `id` und `name`:

```python
from django.db import models


class Customer(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = "customers"
```

`apps/erp/models/__init__.py` importiert `Customer`. Ohne diesen Import registriert Django das Modell nicht.

Lesen, in einem Service der Fach-App, die die Zahl lokal speichert:

```python
from apps.erp.models import Customer


def customer_name(customer_id: int) -> str:
    customer = Customer.objects.get(pk=customer_id)
    return customer.name
```

Der Router wählt `erp`. Ein expliziter Alias ist gleichwertig und nützlich, wenn eine einzelne Abfrage vom Router abweichen soll:

```python
Customer.objects.using("erp").get(pk=customer_id)
```

`using("erp")` gewinnt gegen den Router.

### Migrationen und Prüfung

`make makemigrations erp` erzeugt für `managed = False` eine Migration, die beim Anwenden keine Tabelle baut. `make migrate` läuft gegen `default`. Der Alias `erp` bekommt wegen `allow_migrate` keinen Schema-Lauf.

Verbindung prüfen, ohne eine Tabelle anzufassen. `make shell` öffnet das Backend, dort:

```bash
python manage.py shell -c "from django.db import connections; connections['erp'].ensure_connection(); print('ok')"
```

Derselbe Aufruf ohne interaktive Shell:

```bash
docker compose --env-file docker/.env -f docker/compose.yml exec -T backend \
  python manage.py shell -c "from django.db import connections; connections['erp'].ensure_connection(); print('ok')"
```

`make manage` reicht seine Argumente an `manage.py` weiter. Ein Argument, das mit `-` beginnt, wertet Make als eigene Option. Der gezeigte `shell -c` läuft deshalb als Compose-Befehl und nicht als `make manage shell -c`.

Schlägt das fehl, der Reihe nach: Name in `ERP_DB_HOST` von der VM aus (`getent hosts erp.internal`), Port vom Container aus, Benutzer und Datenbankname, TLS (`ERP_DB_SSLMODE=prefer` nur zum Eingrenzen, auf dem Server danach wieder `require`), Firewall des Drittsystems.

`make check-deploy` und die Tests nutzen die Testdatenbank von `default`. Eine App mit `managed = False` legt in der Testdatenbank keine fremde Tabelle an. Tests für den Service ersetzen `Customer.objects` mit `pytest-mock`, wie [docs/rules/testing.md](../rules/testing.md) es für externe Systeme verlangt. Ein Integrationstest, der das echte Drittsystem braucht, hängt am Netz dieses Systems und gehört nicht in den normalen `make test`.

## Make

`make help` listet jedes Ziel mit dem Kurztext aus der `Makefile`. Die Ziele laufen im Verzeichnis der `Makefile`. Der Dev-Stack muss laufen, sobald das Ziel `docker compose exec` verwendet. Ausnahmen sind `help`, `urls`, `dev`, `up`, `down`, `build`, `rebuild`, `destroy`, `pull`, `config`, `prod`, `create_app`, `create_feature` und `clean-pyc`.

Die Form `make <ziel> <dienst>` gilt für `restart`, `start`, `stop`, `logs`, `build`, `makemigrations` und `manage`. Dienste sind `backend`, `frontend`, `db` und `redis`. `dev` und `all` bedeuten bei `restart`, `start`, `stop`, `logs` und `build` alle passenden Dienste.

### Stack

| Aufruf | Wirkung |
|---|---|
| `make help` | Ziele und Kurztexte |
| `make urls` | Frontend, API, Health, Swagger, Schema, Admin, PostgreSQL und Redis mit den Ports aus `docker/.env` |
| `make dev` | Dev-Stack im Hintergrund. Entspricht `make up` |
| `make up` | wie `make dev` |
| `make down` | Container entfernen, Volumes behalten |
| `make restart` | alle Dienste neu starten |
| `make restart backend` | ein Dienst. Auch `frontend`, `db`, `redis`, `dev` |
| `make start frontend` | gestoppte Container starten |
| `make stop db` | Container stoppen, ohne sie zu entfernen |
| `make ps` | Zustand der Dienste |
| `make logs` | alle Logs, letzte 200 Zeilen, folgt weiter |
| `make logs backend` | Logs eines Dienstes |
| `make config` | Compose-Datei mit eingesetzten Variablen |
| `make pull` | Images von PostgreSQL und Redis ziehen |
| `make destroy` | Container und Volumes löschen. Die Datenbank ist danach leer |
| `make prod` | `docker/compose.prod.yml` mit `docker/.env.prod` bauen und starten |

### Build

| Aufruf | Wirkung |
|---|---|
| `make build` | Images von Backend und Frontend |
| `make build backend` | nur eines der beiden. `frontend` genauso. `db` und `redis` haben kein lokales Image |
| `make rebuild` | beide Images ohne Cache, danach `up -d` |

### Shell

| Aufruf | Wirkung |
|---|---|
| `make shell` | Shell im Backend |
| `make shell frontend` | Shell in einem Dienst. Auch `db` und `redis` |
| `make psql` | `psql` als `POSTGRES_USER` auf `POSTGRES_DB` im Container `db` |
| `make redis-cli` | `redis-cli` im Container `redis`, authentifiziert über `REDISCLI_AUTH` |

### Django

| Aufruf | Wirkung |
|---|---|
| `make migrate` | `manage.py migrate` im Backend |
| `make makemigrations billing` | Migrationen für eine App erzeugen. Ohne Namen prüft Django alle Apps |
| `make createsuperuser` | Superuser interaktiv anlegen |
| `make manage showmigrations` | beliebiges `manage.py`. Ohne Argument bricht das Ziel ab |
| `make check` | `manage.py check` |
| `make check-deploy` | `check --deploy` mit `DEBUG=false`, festem Schlüssel, `ALLOWED_HOSTS=example.com` und SMTP. Warnungen lassen das Ziel scheitern |
| `make check-migrations` | `makemigrations --check --dry-run`. Eine fehlende Migration lässt das Ziel scheitern |
| `make create_app billing` | App auf dem Host anlegen. Der Stack darf stehen oder aus sein. Python 3 auf dem Host |
| `make create_feature billing` | Frontend-Modul auf dem Host anlegen |

`create_app` und `create_feature` nehmen genau einen Namen. Regeln und der weitere Ausbau stehen in [Kapitel 3](03-eigene-implementierung.md).

### Tests und Qualität

Der Stack läuft. pytest legt die Testdatenbank in der Compose-PostgreSQL an.

| Aufruf | Wirkung |
|---|---|
| `make test` | pytest mit Abdeckung von `apps` |
| `make test-unit` | Marker `unit` |
| `make test-integration` | Marker `integration` |
| `make test-api` | Marker `api` |
| `make test-frontend` | Vitest im Frontend-Container |
| `make typecheck` | `tsc --noEmit` im Frontend |
| `make lint` | Ruff und ESLint |
| `make lint-python` | nur Ruff, einschließlich Formatprüfung |
| `make format-python` | Ruff formatiert und wendet die automatischen Fixes an |
| `make format-frontend` | Prettier im Frontend, als Prüfung |
| `make build-frontend` | `next build` im laufenden Dev-Container |
| `make audit` | `pip-audit` für `requirements.txt` und `npm audit` ab Stufe hoch |
| `make install-backend` | `requirements-dev.txt` im Backend-Container installieren |
| `make install-frontend` | `npm ci` im Frontend-Container |
| `make clean-pyc` | `__pycache__` unter `backend/` auf dem Host löschen |
| `make loadtest` | Locust auf dem Host, 100 Benutzer, 10 pro Sekunde, 30 Sekunden |

Locust liest `backend/.venv/bin/locust` und `backend/locustfile.py`. Das Virtuelle Environment liegt auf dem Host, nicht im Image:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements-dev.txt
```

Lauf ändern:

```bash
LOCUST_USERS=10 LOCUST_SPAWN_RATE=2 LOCUST_RUN_TIME=15s make loadtest
```

Das Ziel liest `BACKEND_PORT` aus `docker/.env` und prüft `https://127.0.0.1`. `REQUESTS_CA_BUNDLE` zeigt auf `docker/certs/dev.crt`, damit Locust das selbstsignierte Zertifikat akzeptiert. Ein Backend, das nur im Compose-Netz erreichbar ist, braucht den veröffentlichten Host-Port.

Schichten, Marker und die Ablage der Testdateien stehen in [docs/rules/testing.md](../rules/testing.md).

## Geheimnisse

`docker/.env` und `docker/.env.prod` bleiben außerhalb von Git. Ein Beispielwert, der in eine Vorlage gehört, ist ein Platzhalter wie `replace-this-database-password`. Ein Schlüssel, der einmal auf einer erreichbaren VM galt, wird ersetzt, sobald er in einem Log, einem Ticket oder einer Shell-History stand.

`make config` druckt die aufgelöste Compose-Datei einschließlich der Passwörter. Die Ausgabe bleibt auf der VM.
