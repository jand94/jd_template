import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Legt den Superuser aus den DJANGO_SUPERUSER_*-Umgebungsvariablen an, falls er fehlt."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        missing = [
            name
            for name, value in (
                ("DJANGO_SUPERUSER_USERNAME", username),
                ("DJANGO_SUPERUSER_EMAIL", email),
                ("DJANGO_SUPERUSER_PASSWORD", password),
            )
            if not value
        ]
        if missing:
            raise CommandError("Fehlende Umgebungsvariablen: " + ", ".join(missing))

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' ist bereits vorhanden.")
            return

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' wurde angelegt."))
