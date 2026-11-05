# Eigene Implementierung

Dieses Kapitel baut ein Fachmodul von der leeren App bis zur Seite im Browser. Das Beispiel heißt `billing` und verwaltet Rechnungen in der Anwendungsdatenbank. Ein zweiter Teil liest einen Kundenbestand aus einem Drittsystem, mit dem Alias aus [Kapitel 2](02-umgebung-und-befehle.md).

Die Form, die dabei entsteht, ist die aus [docs/rules/ordnerstruktur.md](../rules/ordnerstruktur.md). Antworten, Rechte und Seiten folgen [docs/rules/api.md](../rules/api.md). Tests folgen [docs/rules/testing.md](../rules/testing.md).

Zwei Generatoren legen das Gerüst. Sie laufen auf dem Host mit Python 3 und brauchen keinen laufenden Stack:

```bash
make create_app billing
make create_feature billing
```

Der Name beginnt mit einem Kleinbuchstaben und enthält nur Kleinbuchstaben, Ziffern und Unterstriche. Reserviert für Apps sind `apps`, `backend`, `config`, `django`, `test` und `tests`, dazu jedes Python-Schlüsselwort. Reserviert für Features sind zusätzlich die bestehenden Routen, darunter `accounts`, `anmelden`, `dashboard`, `profil` und `system`. Die vollständige Liste steht in `scripts/create_feature.py`.

App und Feature tragen denselben Namen, bleiben aber getrennte Module. Eine App importiert keine andere App über deren interne Module. Ein Feature importiert kein anderes Feature. Die öffentliche Tür der App ist ihre HTTP-API, die des Features ist `index.ts`.

## Was die Generatoren anlegen

`scripts/create_app.py` erzeugt `backend/apps/billing/` mit Admin, `api/v1` (Permissions, Schema, Serializer, Services, Views), Exceptions, Migrationen, Models, Services und den Testordnern `unit`, `integration` und `api`. Jeder Ordner ist ein Paket mit `__init__.py`.

Danach trägt das Skript `apps.billing.apps.BillingConfig` im Abschnitt `interne Apps` von `INSTALLED_APPS` ein und hängt in `backend/backend/urls.py` diese Zeile an:

```python
path("billing/", include("apps.billing.urls")),
```

`apps/billing/urls.py` bindet die Version ein. Der Generator setzt keinen `app_name`. Accounts tut das, damit `reverse` den Namen eindeutig unter der App findet. Dieselbe Zeile kommt in `apps/billing/urls.py`:

```python
app_name = "billing"

urlpatterns = [
    path("v1/", include("apps.billing.api.v1.urls")),
]
```

Die HTTP-Basis ist damit `/billing/v1/`. Eine spätere Version ist ein Geschwisterpaket von `api/v1` und bekommt in `apps/billing/urls.py` einen eigenen `path`. Routen einer Version stehen nur in `api/<version>/urls.py`.

`scripts/create_feature.py` erzeugt `frontend/src/features/billing/` mit `api/client.ts`, `components/screen.tsx`, leeren Ordnern `hooks`, `schemas` und `types`, und `index.ts` als einzige öffentliche Tür. Die Route `frontend/src/app/(app)/billing/page.tsx` rendert `BillingScreen`. Die Gruppe `(app)` verlangt eine Sitzung und fehlt in der URL. Die Seite liegt unter `/billing`.

Der Client spricht denselben Ursprung wie der Browser:

```ts
export const api = createApiClient("/billing/v1");
```

`createApiClient` aus `frontend/src/lib/api.ts` holt das CSRF-Cookie über `/accounts/v1/csrf`, sendet `X-CSRFToken`, liest Fehlerfelder und wirft `ApiError`. Ein neues Modul bekommt dafür keinen eigenen CSRF-Endpunkt.

## Was die Generatoren offen lassen

Der Stack zeigt nach den beiden Befehlen eine leere Überschrift und eine leere URLconf. Damit aus dem Modul eine Funktion wird, kommen diese Stücke dazu. Die Reihenfolge ist die, in der Django und Next.js sie brauchen.

1. Modell in `apps/billing/models`, importiert in `models/__init__.py`.
2. Migration, `make makemigrations billing` und `make migrate`.
3. Domänenfunktion in `apps/billing/services`, importiert in `services/__init__.py`.
4. Serializer in `api/v1/serializers`, importiert im Paket-`__init__.py`.
5. View in `api/v1/views`, importiert im Paket-`__init__.py`.
6. Pfad in `api/v1/urls.py`.
7. OpenAPI-Schema neben der View.
8. Admin, sobald jemand den Bestand im Django-Admin pflegt.
9. Tests in `tests/unit`, `tests/api` und, sobald Persistenz und Rechte zusammenwirken, `tests/integration`.
10. Proxy `frontend/src/app/billing/[...path]/route.ts`, sonst erreicht der Browser Django nicht.
11. Aufruf im Feature über `features/billing/api/client.ts`.
12. Eintrag in `frontend/src/config/navigation.ts`, sonst bleibt die Seite ohne Menüpunkt.

`accounts` ist das ausgebaute Muster für jeden dieser Punkte: Modelle unter `backend/apps/accounts/models`, Services unter `backend/apps/accounts/services`, HTTP unter `backend/apps/accounts/api/v1`, der Browser unter `frontend/src/features/accounts`.

## Modell

`backend/apps/billing/models/invoice.py`:

```python
from django.conf import settings
from django.db import models


class Invoice(models.Model):
    number = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=200)
    amount_cents = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
```

`AUTH_USER_MODEL` ist `accounts.User`. Der Verweis läuft über diese Einstellung, nicht über einen Import von `apps.accounts.models` in ein anderes Fachmodul, wenn sich das vermeiden lässt. `settings.AUTH_USER_MODEL` hält die Abhängigkeit an Django.

`backend/apps/billing/models/__init__.py` registriert das Modell. Django findet es nur über diesen Import:

```python
from apps.billing.models.invoice import Invoice

__all__ = ["Invoice"]
```

Der Stack läuft.

```bash
make makemigrations billing
make migrate
make check-migrations
```

`makemigrations` schreibt nach `backend/apps/billing/migrations/`. Die Datei gehört ins Repository. `check-migrations` scheitert, wenn ein Modell und die Migrationen auseinanderlaufen.

## Service

Domänenregeln liegen in `apps/billing/services`, nicht in der View. Die View prüft den Eingang, ruft den Service und gibt das Ergebnis aus.

`backend/apps/billing/services/invoices.py`:

```python
from django.db import transaction

from apps.billing.models import Invoice


@transaction.atomic
def create_invoice(*, number: str, title: str, amount_cents: int, user) -> Invoice:
    return Invoice.objects.create(
        number=number,
        title=title,
        amount_cents=amount_cents,
        created_by=user,
    )
```

`backend/apps/billing/services/__init__.py`:

```python
from apps.billing.services.invoices import create_invoice

__all__ = ["create_invoice"]
```

Andere Apps importieren höchstens diesen Paketnamen, wenn eine Grenze wirklich überschritten werden muss. Interna (`services/invoices.py`, Modelle fremder Apps) bleiben auf der anderen Seite der Grenze.

## Serializer, View, URL

Serializer beschreiben den Körper. Schreibfelder und Lesefelder sind getrennt, wie `UserSerializer` und `UserUpdateSerializer` unter Accounts.

`backend/apps/billing/api/v1/serializers/invoice.py`:

```python
from rest_framework import serializers

from apps.billing.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "number", "title", "amount_cents", "created_at"]
        read_only_fields = fields


class InvoiceCreateSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=32)
    title = serializers.CharField(max_length=200)
    amount_cents = serializers.IntegerField(min_value=0)
```

`backend/apps/billing/api/v1/serializers/__init__.py` importiert beide Klassen und listet sie in `__all__`.

Öffentliche Endpunkte setzen `permission_classes` ausdrücklich auf `AllowAny`. Alles andere verlangt eine Sitzung, weil `DEFAULT_PERMISSION_CLASSES` auf `IsAuthenticated` steht. Billing bleibt bei dieser Vorgabe. Zusätzlich sieht ein Benutzer nur eigene Rechnungen.

`backend/apps/billing/api/v1/views/invoices.py`:

```python
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from apps.billing.api.v1.serializers import InvoiceCreateSerializer, InvoiceSerializer
from apps.billing.models import Invoice
from apps.billing.services import create_invoice


class InvoiceListCreateView(ListCreateAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(created_by=self.request.user)

    def post(self, request):
        incoming = InvoiceCreateSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        invoice = create_invoice(user=request.user, **incoming.validated_data)
        return Response(InvoiceSerializer(invoice).data, status=201)
```

`ListCreateAPIView` paginiert über `PagePagination`: Körper `count`, `next`, `previous`, `results`. Die Seite steht in `page`, die Größe in `page_size`, höchstens 100, Standard 20.

Schema neben den Accounts-Views, in `backend/apps/billing/api/v1/schema/invoices.py`, mit `drf_spectacular`. Die Accounts-Datei `backend/apps/accounts/api/v1/schema/accounts.py` zeigt `extend_schema` als Hilfsfunktion. Ein kurzer Eintrag in `SPECTACULAR_SETTINGS["TAGS"]` in `settings.py` gibt der Gruppe einen Text in Swagger:

```python
{"name": "Billing", "description": "Rechnungen des angemeldeten Kontos."},
```

Die View hängt den Tag über `extend_schema(tags=["Billing"])`.

`backend/apps/billing/api/v1/views/__init__.py` exportiert `InvoiceListCreateView`. `backend/apps/billing/api/v1/urls.py`:

```python
from django.urls import path

from apps.billing.api.v1.views import InvoiceListCreateView

urlpatterns = [
    path("invoices/", InvoiceListCreateView.as_view(), name="invoice-list"),
]
```

Der Name `invoice-list` ist das Ziel von `reverse` in den Tests. Die volle Route ist `/billing/v1/invoices/`.

Fehler, die der Client als `ApiError` liest, haben die Form aus [docs/rules/api.md](../rules/api.md): `detail` ist ein String, jedes weitere Feld eine Liste von Strings. `raise_exception=True` am Serializer erzeugt genau das für ungültige Körper.

Eine fachliche Ablehnung wirft im Service `django.core.exceptions.ValidationError`, so wie `apps.accounts.services`. Die View fängt sie und wirft `rest_framework.exceptions.ValidationError`, so wie `apps.accounts.api.v1.views.auth`. Erst diese DRF-Ausnahme formt der Handler in `apps.api.errors` auf den Körper, den der Client liest. Eine unbehandelte Python-Ausnahme antwortet mit Status 500 und `{"detail": "Die Anfrage ist fehlgeschlagen."}`. Der Log enthält die Ursache, der Körper nicht. Klassen in `apps/billing/exceptions` benennen die Fälle für Services und Tests. Sie ersetzen die Übersetzung in der View nicht.

## Admin

`backend/apps/billing/admin/invoice.py` registriert `Invoice`. `admin/__init__.py` importiert das Modul, sonst lädt Django die Registrierung nicht. Accounts macht dasselbe mit `admin/user.py`. Der Admin hängt am Backend-Port unter `/admin/` und nutzt dieselbe Sitzung wie das Frontend, wenn beide über denselben Hostnamen erreichbar sind.

## Tests

Ein Unit-Test prüft `create_invoice` ohne HTTP. Ein API-Test prüft den Endpunkt über `api_client` aus `backend/conftest.py`. Die Testdatenbank legt pytest in der Compose-PostgreSQL an. Der Stack läuft.

`backend/apps/billing/tests/unit/test_invoices.py` bleibt ohne Datenbank. Der Service wird an der Stelle geprüft, an der er das Modell aufruft:

```python
from unittest.mock import patch

import pytest

from apps.billing.services import create_invoice

pytestmark = pytest.mark.unit


def test_create_invoice_stores_the_signed_in_user():
    user = object()
    with patch("apps.billing.services.invoices.Invoice.objects.create") as create:
        create_invoice(number="R-1", title="Beratung", amount_cents=100, user=user)
    assert create.call_args.kwargs["created_by"] is user
```

Persistenz gehört in `tests/integration` mit `@pytest.mark.integration` und `@pytest.mark.django_db`. Der API-Test:

```python
import pytest
from django.urls import reverse

pytestmark = [pytest.mark.api, pytest.mark.django_db]


def test_invoice_list_requires_session(api_client):
    response = api_client.get(reverse("billing:invoice-list"))
    assert response.status_code == 401
```

`reverse("billing:invoice-list")` gilt, sobald `apps/billing/urls.py` den `app_name` setzt. `api_client.force_authenticate(user=user)` setzt die Sitzung für den eigentlichen Ablauf. Benutzer kommen aus `apps.api.tests.factories.UserFactory` oder aus einer Factory in `apps/billing/tests/factories.py`, sobald die App eigene Modelle baut. Eine Factory erbt `factory.django.DjangoModelFactory`.

```bash
make test-unit
make test-api
make check-migrations
```

Die Abdeckung gilt für `apps` und lässt `migrations` und `tests` aus. Unter der Schwelle in `.coveragerc` scheitert `make test`.

## Proxy zum Backend

Der Browser ruft `/billing/v1/invoices/` auf dem Frontend auf. Next.js kennt diese URL nur als Seite oder als Route-Handler. Die Seite liegt unter `/billing`. Die API braucht einen Handler, der an Django weiterleitet. Für Accounts leistet das `frontend/src/app/accounts/[...path]/route.ts`. Billing bekommt dieselbe Datei unter `frontend/src/app/billing/[...path]/route.ts`.

Der Handler liegt neben den Routengruppen `(app)` und `(public)`, nicht darin. `[...path]` verlangt mindestens ein Segment. `/billing` bleibt die Seite, `/billing/v1/invoices/` trifft den Handler.

Die Datei übernimmt den Accounts-Proxy und ersetzt die Zielbasis:

```ts
const target = new URL(`/billing/${path.join("/")}/`, apiOrigin);
```

`apiOrigin` bleibt `process.env.API_ORIGIN ?? "http://backend:8000"`. Header, Cookies und der Umgang mit Status 204 bleiben wie bei Accounts. Die Liste `forwardedRequestHeaders` enthält `origin`, `referer` und `x-forwarded-proto`. Der Dev-Proxy und der Nginx der Produktion setzen `X-Forwarded-Proto: https`. Ohne diese drei Namen sieht Django die Browser-Adresse nicht und lehnt die Sitzung ab, sobald die Anfrage als HTTPS gilt.

Ohne diese Datei antwortet Next.js auf den API-Aufruf mit 404, während `curl` gegen den Backend-Port dieselbe Route findet. Swagger unter `/api/docs/` spricht Django direkt und umgeht den Proxy ebenfalls.

Nach dem Anlegen der Datei lädt der Dev-Server neu. Ein Produktions-Image enthält sie erst nach `make prod`.

## Oberfläche

`frontend/src/features/billing/components/screen.tsx` ist eine Client-Komponente, sobald sie lädt oder Formularzustand hält. `"use client"` steht nur in dieser Datei. Die Seite `app/(app)/billing/page.tsx` bleibt eine Server Component und importiert das Feature ausschließlich über den Barrel:

```tsx
import { BillingScreen } from "@/features/billing";

export default function Page() {
  return <BillingScreen />;
}
```

Aufruf über den vorbereiteten Client. `send` und `parse` kommen von `createApiClient`:

```tsx
"use client";

import { useEffect, useState } from "react";

import { api } from "@/features/billing/api/client";

type Invoice = {
  id: number;
  number: string;
  title: string;
  amount_cents: number;
  created_at: string;
};

type InvoicePage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Invoice[];
};

export function BillingScreen() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const body = await api.parse<InvoicePage>(await api.send("/invoices/", "GET"));
      if (!cancelled) {
        setInvoices(body.results);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section>
      <h1 className="text-3xl font-semibold tracking-tight">Rechnungen</h1>
      <ul>
        {invoices.map((invoice) => (
          <li key={invoice.id}>
            {invoice.number} {invoice.title}
          </li>
        ))}
      </ul>
    </section>
  );
}
```

`api.send("/invoices/", "GET")` wird zu `/billing/v1/invoices/`. Ein leerer oder `"/"`-Pfad träfe die Basis selbst. Fehler wirft `parse` als `ApiError` mit `status` und `fields`.

Typen, die nur dieses Modul braucht, liegen unter `features/billing/types`. Zod-Schemata für Formulare liegen unter `features/billing/schemas`. Beides exportiert `index.ts` nur, wenn eine andere Datei derselben App es über den Barrel brauchen soll. Seiten außerhalb des Features importieren weiterhin nur, was `index.ts` exportiert.

Menüpunkt in `frontend/src/config/navigation.ts`. Die Datei importiert kein Feature. Sie nennt nur Adresse und Beschriftung:

```ts
export const primaryNavigation: NavigationItem[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/billing", label: "Rechnungen" },
  { href: "/system", label: "System" },
];
```

Header und Fußzeile lesen `primaryNavigation` und zeigen den Eintrag in der App-Shell.

Prüfung im laufenden Stack:

```bash
make typecheck
make lint
make test-frontend
```

Ein Vitest für die Oberfläche liegt neben der Komponente als `screen.test.tsx` und rendert mit `@testing-library/react`. Accounts hat das Muster in `password-set-form.test.tsx`.

## Kunden aus einem Drittsystem

Der Alias `erp`, der Router und das unverwaltete Modell `Customer` stehen in [Kapitel 2](02-umgebung-und-befehle.md). Billing speichert den fremden Schlüssel lokal und fragt den Namen beim Lesen nach.

Am Modell `Invoice` ein Feld ohne ForeignKey über die Alias-Grenze:

```python
customer_id = models.IntegerField()
```

Neue Migration mit `make makemigrations billing`. Der Service nimmt `customer_id` entgegen, liest `Customer` über den Router und legt die Rechnung in `default` an:

```python
from django.core.exceptions import ValidationError

from apps.erp.models import Customer


def create_invoice(*, number, title, amount_cents, customer_id, user) -> Invoice:
    if not Customer.objects.filter(pk=customer_id).exists():
        raise ValidationError({"customer_id": "Der Kunde ist im Bestand nicht vorhanden."})
    return Invoice.objects.create(
        number=number,
        title=title,
        amount_cents=amount_cents,
        customer_id=customer_id,
        created_by=user,
    )
```

`ValidationError` kommt aus `django.core.exceptions`. Die View übersetzt sie in die DRF-`ValidationError`, dann antwortet der Endpunkt mit 400 und dem Feld `customer_id`. Der Unit-Test ersetzt `Customer.objects` und prüft die Ablehnung, ohne das Drittsystem zu erreichen.

Der Serializer nimmt `customer_id` im Schreibkörper auf und gibt es im Lesekörper mit aus. Der Anzeigename kommt aus dem Service als zusätzliches Feld, das der Serializer aus dem Kontext setzt, oder aus einem zweiten Lesezugriff in der View. Ein Join von `Invoice` auf `Customer` ist nicht möglich, weil die Tabellen in verschiedenen Datenbanken liegen.

## Grenze zwischen den Modulen

| Richtung | Erlaubt |
|---|---|
| Seite importiert `@/features/billing` | ja, nur den Barrel |
| Feature importiert `@/features/accounts` | nein. ESLint-Regel `features/boundaries` |
| `components/`, `lib/`, `config/` importieren ein Feature | nein |
| App importiert `apps.accounts.models` aus einer anderen App | nur über eine öffentliche Funktion in `apps.accounts.services`, und auch das nur, wenn die Fachlichkeit es verlangt |
| HTTP-Schicht importiert `apps.billing.services` | ja |
| Service importiert einen Serializer | nein. Die Richtung läuft von der View zum Service |

Eine gemeinsame Hilfsfunktion ohne Fachlichkeit liegt in der App, die sie besitzt, oder in einem Modul unter `backend/backend`, wenn sie zur Projektkonfiguration gehört. Ein neues Querschnittsmodul entsteht mit `make create_app`, nicht als Importnetz zwischen Features.

## Checkliste vor dem ersten echten Datensatz

- `models/__init__.py`, `services/__init__.py`, `serializers/__init__.py` und `views/__init__.py` importieren die neuen Namen.
- `make check-migrations` ist ruhig.
- `GET /billing/v1/invoices/` ohne Sitzung antwortet 401.
- Dieselbe URL über das Frontend, mit Sitzung, liefert `results`.
- Der Proxy reicht in der Produktion `x-forwarded-proto` weiter.
- `make test` und `make typecheck` laufen durch.
- Ein Drittsystem-Modell trägt `managed = False`, der Router gibt für seinen Alias `allow_migrate` mit `False` zurück, und der Datenbankbenutzer dort darf nur lesen, solange das Modul nur liest.
