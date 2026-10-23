#!/usr/bin/env python3
"""Legt eine Django-App unter backend/apps/<name> an und registriert sie."""

import keyword
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
APPS = BACKEND / "apps"
SETTINGS = BACKEND / "backend" / "settings.py"
URLS = BACKEND / "backend" / "urls.py"

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED = {"apps", "backend", "config", "django", "test", "tests"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def config_class(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_")) + "Config"


def insert_before_list_end(text: str, list_name: str, entry: str) -> str:
    match = re.search(rf"({list_name} = \[.*?)(\n\])", text, re.S)
    if match is None:
        fail(f"{list_name} wurde nicht gefunden.")
    if entry.strip() in match.group(1):
        fail(f"{entry.strip()} ist bereits eingetragen.")
    return text[: match.end(1)] + "\n" + entry + text[match.start(2) :]


def insert_internal_app(text: str, entry: str) -> str:
    match = re.search(r"(INSTALLED_APPS = \[.*?# interne Apps\n)(.*?)(\n\])", text, re.S)
    if match is None:
        fail("Abschnitt '# interne Apps' fehlt in INSTALLED_APPS.")
    if entry.strip() in match.group(2):
        fail(f"{entry.strip()} ist bereits eingetragen.")
    return text[: match.end(2)] + "\n" + entry + text[match.start(3) :]


def main() -> None:
    if len(sys.argv) != 2:
        fail("Aufruf: make create_app <appname>")

    name = sys.argv[1]
    if keyword.iskeyword(name) or name in RESERVED:
        fail(f"'{name}' ist als App-Name reserviert.")
    if not NAME_RE.fullmatch(name):
        fail(
            "App-Name muss mit einem Kleinbuchstaben beginnen und darf nur "
            "Kleinbuchstaben, Ziffern und Unterstriche enthalten."
        )

    app_dir = APPS / name
    if app_dir.exists():
        fail(f"apps/{name} gibt es bereits.")

    class_name = config_class(name)
    config_path = f"apps.{name}.apps.{class_name}"
    packages = [
        app_dir,
        app_dir / "admin",
        app_dir / "api",
        app_dir / "api" / "v1",
        app_dir / "api" / "v1" / "permissions",
        app_dir / "api" / "v1" / "schema",
        app_dir / "api" / "v1" / "serializers",
        app_dir / "api" / "v1" / "services",
        app_dir / "api" / "v1" / "views",
        app_dir / "exceptions",
        app_dir / "migrations",
        app_dir / "models",
        app_dir / "services",
        app_dir / "tests",
        app_dir / "tests" / "unit",
        app_dir / "tests" / "integration",
        app_dir / "tests" / "api",
    ]
    for package in packages:
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    (app_dir / "models" / "__init__.py").write_text(
        "# Modelmodule hier importieren, damit Django sie registriert.\n",
        encoding="utf-8",
    )
    (app_dir / "apps.py").write_text(
        "from django.apps import AppConfig\n"
        "\n"
        "\n"
        f"class {class_name}(AppConfig):\n"
        f"    name = 'apps.{name}'\n"
        f"    label = '{name}'\n",
        encoding="utf-8",
    )
    (app_dir / "urls.py").write_text(
        "from django.urls import include, path\n"
        "\n"
        "urlpatterns = [\n"
        f"    path('v1/', include('apps.{name}.api.v1.urls')),\n"
        "]\n",
        encoding="utf-8",
    )
    (app_dir / "api" / "v1" / "urls.py").write_text(
        "urlpatterns = [\n"
        "]\n",
        encoding="utf-8",
    )

    settings = SETTINGS.read_text(encoding="utf-8")
    settings = insert_internal_app(settings, f"    '{config_path}',")
    SETTINGS.write_text(settings, encoding="utf-8")

    urls = URLS.read_text(encoding="utf-8")
    urls = insert_before_list_end(
        urls,
        "urlpatterns",
        f"    path('{name}/', include('apps.{name}.urls')),",
    )
    URLS.write_text(urls, encoding="utf-8")

    print(f"App {name} angelegt, registriert und unter /{name}/v1/ eingehängt.")


if __name__ == "__main__":
    main()
