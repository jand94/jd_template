"use client";

import Link from "next/link";
import { KeyRound, LogIn, Mail, MailCheck } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Icon } from "@/components/ui/icon";
import { ApiError, fieldMessage, requestPasswordReset } from "@/features/accounts/api/session";
import { AuthPanel } from "@/features/accounts/components/auth-panel";
import { FormError, FormStatus, SubmitButton, TextField } from "@/features/accounts/components/fields";

export function PasswordResetForm() {
  const [email, setEmail] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [sent, setSent] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch (caught) {
      setError(caught);
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthPanel
      icon={KeyRound}
      title="Passwort vergessen"
      description="Wenn ein Konto zu dieser E-Mail existiert, senden wir einen Hinweis."
      footer={
        <Link href="/anmelden" className="inline-flex min-h-11 items-center gap-2 text-sm font-medium text-foreground hover:text-accent">
          <Icon icon={LogIn} />
          Zurück zur Anmeldung
        </Link>
      }
    >
      {sent ? (
        <FormStatus>
          <Icon icon={MailCheck} />
          Die Anfrage ist eingegangen. Prüfe das Postfach, falls ein Konto dazu existiert.
        </FormStatus>
      ) : (
        <form className="flex flex-col gap-5" onSubmit={onSubmit}>
          <FormError>{error instanceof ApiError && Object.keys(error.fields).length === 0 ? error.message : null}</FormError>
          <TextField
            label="E-Mail"
            name="email"
            type="email"
            autoComplete="email"
            icon={Mail}
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            error={fieldMessage(error, "email")}
          />
          <SubmitButton pending={pending}>Hinweis senden</SubmitButton>
        </form>
      )}
    </AuthPanel>
  );
}
