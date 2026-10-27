from django.db import migrations, models
import django.db.models.functions

import apps.accounts.models.validators


def lowercase_emails(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    seen = {}
    for user in User.objects.all().only("id", "email").iterator():
        normalized = (user.email or "").strip().casefold()
        if not normalized:
            raise ValueError(f"User {user.pk} has an empty email and cannot be migrated.")
        previous = seen.get(normalized)
        if previous is not None:
            raise ValueError(
                "Cannot lowercase emails: "
                f"users {previous} and {user.pk} both map to {normalized!r}."
            )
        seen[normalized] = user.pk
        if user.email != normalized:
            User.objects.filter(pk=user.pk).update(email=normalized)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(lowercase_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                upload_to="accounts/avatars/%Y/%m/",
                validators=[apps.accounts.models.validators.validate_avatar],
                verbose_name="avatar",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                django.db.models.functions.Lower("email"),
                name="user_email_ci_unique",
            ),
        ),
    ]
