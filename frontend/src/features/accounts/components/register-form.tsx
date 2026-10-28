"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { KeyRound, LogIn, Mail, UserRound } from "lucide-react";
import { useId, useState, type FormEvent } from "react";
import { Icon } from "@/components/ui/icon";
import { ApiError, fieldMessage, register } from "@/features/accounts/api/session";
import { AuthPanel } from "@/features/accounts/components/auth-panel";
import { FormError, SubmitButton, TextField } from "@/features/accounts/components/fields";
import { useAccount } from "@/features/accounts/hooks/account-context";

export function RegisterForm() {
  const router = useRouter();
  const account = useAccount();
  const termsId = useId();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const user = await register({
        username,
        email,
        password,
        password_confirm: passwordConfirm,
        first_name: firstName,
        last_name: lastName,
        terms_accepted: termsAccepted,
      });
      account.setUser(user);
      router.push("/dashboard");
    } catch (caught) {
      setError(caught);
      setPending(false);
    }
  }

  const formError = error instanceof ApiError && Object.keys(error.fields).length === 0 ? error.message : null;
  const termsError = fieldMessage(error, "terms_accepted");

  return (
    <AuthPanel
      icon={UserRound}
      title="Registrieren"
      description="Ein Konto anlegen und direkt angemeldet bleiben."
      footer={
        <Link href="/anmelden" className="inline-flex min-h-11 items-center gap-2 text-sm font-medium text-foreground hover:text-accent">
          <Icon icon={LogIn} />
          Schon ein Konto? Anmelden
        </Link>
      }
    >
      <form className="flex flex-col gap-5" onSubmit={onSubmit} noValidate>
        <FormError>{formError}</FormError>
        <TextField
          label="Benutzername"
          name="username"
          autoComplete="username"
          icon={UserRound}
          required
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          error={fieldMessage(error, "username")}
        />
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
        <div className="grid gap-5 sm:grid-cols-2">
          <TextField
            label="Vorname"
            name="first_name"
            autoComplete="given-name"
            value={firstName}
            onChange={(event) => setFirstName(event.target.value)}
            error={fieldMessage(error, "first_name")}
          />
          <TextField
            label="Nachname"
            name="last_name"
            autoComplete="family-name"
            value={lastName}
            onChange={(event) => setLastName(event.target.value)}
            error={fieldMessage(error, "last_name")}
          />
        </div>
        <TextField
          label="Passwort"
          name="password"
          type="password"
          autoComplete="new-password"
          icon={KeyRound}
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
          icon={KeyRound}
          required
          value={passwordConfirm}
          onChange={(event) => setPasswordConfirm(event.target.value)}
          error={fieldMessage(error, "password_confirm")}
        />
        <div className="flex flex-col gap-2">
          <label htmlFor={termsId} className="flex min-h-11 items-center gap-3 text-sm">
            <input
              id={termsId}
              name="terms_accepted"
              type="checkbox"
              checked={termsAccepted}
              onChange={(event) => setTermsAccepted(event.target.checked)}
              className="size-5 accent-accent"
              aria-invalid={termsError ? true : undefined}
              aria-describedby={termsError ? `${termsId}-error` : undefined}
            />
            Bedingungen akzeptieren
          </label>
          {termsError ? (
            <p id={`${termsId}-error`} className="text-sm text-danger">
              {termsError}
            </p>
          ) : null}
        </div>
        <SubmitButton pending={pending}>Registrieren</SubmitButton>
      </form>
    </AuthPanel>
  );
}
