#!/usr/bin/env python3
"""Legt ein Frontend-Feature unter frontend/src/features/<name> an."""

import keyword
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend" / "src"
FEATURES = FRONTEND / "features"
APP = FRONTEND / "app" / "(app)"

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
RESERVED = {
    "accounts",
    "anmelden",
    "app",
    "components",
    "config",
    "dashboard",
    "features",
    "lib",
    "media",
    "passwort-vergessen",
    "profil",
    "registrieren",
    "system",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def type_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def main() -> None:
    if len(sys.argv) != 2:
        fail("Aufruf: make create_feature <name>")

    name = sys.argv[1]
    if keyword.iskeyword(name) or name in RESERVED or "-" in name:
        fail(f"'{name}' ist als Feature-Name reserviert.")
    if not NAME_RE.fullmatch(name):
        fail(
            "Feature-Name muss mit einem Kleinbuchstaben beginnen und darf nur "
            "Kleinbuchstaben, Ziffern und Unterstriche enthalten."
        )

    feature_dir = FEATURES / name
    if feature_dir.exists():
        fail(f"features/{name} gibt es bereits.")

    page = APP / name / "page.tsx"
    if page.exists():
        fail(f"Die Route /{name} gibt es bereits.")

    screen = f"{type_name(name)}Screen"
    for folder in ("api", "components", "hooks", "schemas", "types"):
        (feature_dir / folder).mkdir(parents=True)

    (feature_dir / "components" / "screen.tsx").write_text(
        f"export function {screen}() {{\n"
        f"  return <h1 className=\"text-3xl font-semibold tracking-tight\">{name}</h1>;\n"
        "}\n",
        encoding="utf-8",
    )
    (feature_dir / "api" / "client.ts").write_text(
        "import { createApiClient } from \"@/lib/api\";\n"
        "\n"
        f"export const api = createApiClient(\"/{name}/v1\");\n",
        encoding="utf-8",
    )
    (feature_dir / "index.ts").write_text(
        f"export {{ {screen} }} from \"@/features/{name}/components/screen\";\n",
        encoding="utf-8",
    )
    for folder in ("hooks", "schemas", "types"):
        (feature_dir / folder / ".gitkeep").write_text("", encoding="utf-8")

    page.parent.mkdir(parents=True)
    page.write_text(
        f"import {{ {screen} }} from \"@/features/{name}\";\n"
        "\n"
        "export default function Page() {\n"
        f"  return <{screen} />;\n"
        "}\n",
        encoding="utf-8",
    )

    print(f"Feature {name} angelegt. Route: /{name}. Öffentliche Schnittstelle: @/features/{name}.")


if __name__ == "__main__":
    main()
