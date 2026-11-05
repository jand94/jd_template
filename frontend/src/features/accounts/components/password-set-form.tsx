"use client";

import Link from "next/link";
import { KeyRound, LogIn } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Icon } from "@/components/ui/icon";
import { ApiError, confirmPasswordReset, fieldMessage } from "@/features/accounts/api/session";
import { AuthPanel } from "@/features/accounts/components/auth-panel";
import {
  FormError,
  FormStatus,
  SubmitButton,
  TextField,
} from "@/features/accounts/components/fields";

export function PasswordSetForm({ uid, token }: { uid: string; token: string }) {
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [saved, setSaved] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await confirmPasswordReset({
        uid,
        token,
        password,
        password_confirm: passwordConfirm,
      });
      setSaved(true);
    } catch (caught) {
      setError(caught);
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthPanel
      icon={KeyRound}
      title="Neues Passwort"
      description="Wähle ein Passwort für dieses Konto."
      footer={
        <Link
          href="/anmelden"
          className="inline-flex min-h-11 items-center gap-2 text-sm font-medium text-foreground hover:text-accent"
        >
          <Icon icon={LogIn} />
          Zur Anmeldung
        </Link>
      }
    >
      {!uid || !token ? (
        <FormError>Der Link ist unvollständig.</FormError>
      ) : saved ? (
        <FormStatus>Das Passwort ist gespeichert. Die Anmeldung verwendet es ab jetzt.</FormStatus>
      ) : (
        <form className="flex flex-col gap-5" onSubmit={onSubmit}>
          <FormError>
            {error instanceof ApiError && Object.keys(error.fields).length === 0
              ? error.message
              : null}
          </FormError>
          <TextField
            label="Neues Passwort"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            error={fieldMessage(error, "password")}
          />
          <TextField
            label="Passwort wiederholen"
            name="password_confirm"
            type="password"
            autoComplete="new-password"
            required
            value={passwordConfirm}
            onChange={(event) => setPasswordConfirm(event.target.value)}
            error={fieldMessage(error, "password_confirm") ?? fieldMessage(error, "token")}
          />
          <SubmitButton pending={pending}>Passwort speichern</SubmitButton>
        </form>
      )}
    </AuthPanel>
  );
}
