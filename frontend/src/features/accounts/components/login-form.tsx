"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { KeyRound, LogIn, UserRound } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Icon } from "@/components/ui/icon";
import { ApiError, fieldMessage, login } from "@/features/accounts/api/session";
import { AuthPanel } from "@/features/accounts/components/auth-panel";
import { FormError, SubmitButton, TextField } from "@/features/accounts/components/fields";
import { useAccount } from "@/features/accounts/hooks/account-context";

export function LoginForm() {
  const router = useRouter();
  const account = useAccount();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const user = await login(username, password);
      account.setUser(user);
      router.push("/profil");
    } catch (caught) {
      setError(caught);
      setPending(false);
    }
  }

  const formError = error instanceof ApiError && Object.keys(error.fields).length === 0 ? error.message : null;

  return (
    <AuthPanel
      icon={LogIn}
      title="Anmelden"
      description="Mit Benutzername und Passwort eine Sitzung starten."
      footer={
        <p className="flex flex-col gap-1 text-sm sm:flex-row sm:items-center sm:justify-between">
          <Link href="/passwort-vergessen" className="inline-flex min-h-11 items-center gap-2 font-medium text-foreground hover:text-accent">
            <Icon icon={KeyRound} />
            Passwort vergessen
          </Link>
          <Link href="/registrieren" className="inline-flex min-h-11 items-center gap-2 font-medium text-foreground hover:text-accent">
            <Icon icon={UserRound} />
            Konto anlegen
          </Link>
        </p>
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
          label="Passwort"
          name="password"
          type="password"
          autoComplete="current-password"
          icon={KeyRound}
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={fieldMessage(error, "password")}
        />
        <SubmitButton pending={pending}>Anmelden</SubmitButton>
      </form>
    </AuthPanel>
  );
}
