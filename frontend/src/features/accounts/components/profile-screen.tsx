"use client";

import Link from "next/link";
import { Check, KeyRound, Mail, UserRound } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Icon } from "@/components/ui/icon";
import { PageIntro } from "@/components/ui/page-intro";
import { panelClass } from "@/components/ui/styles";
import {
  ApiError,
  changePassword,
  fieldMessage,
  updateProfile,
} from "@/features/accounts/api/session";
import { FormError, FormStatus, SubmitButton, TextField } from "@/features/accounts/components/fields";
import { useAccount } from "@/features/accounts/hooks/account-context";

export function ProfileScreen() {
  const account = useAccount();

  if (!account.user) {
    return null;
  }

  return <ProfileForms user={account.user} onUser={account.setUser} />;
}

function ProfileForms({
  user,
  onUser,
}: {
  user: NonNullable<ReturnType<typeof useAccount>["user"]>;
  onUser: (user: NonNullable<ReturnType<typeof useAccount>["user"]>) => void;
}) {
  const [email, setEmail] = useState(user.email);
  const [firstName, setFirstName] = useState(user.first_name);
  const [lastName, setLastName] = useState(user.last_name);
  const [profileError, setProfileError] = useState<unknown>(null);
  const [profilePending, setProfilePending] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [passwordError, setPasswordError] = useState<unknown>(null);
  const [passwordPending, setPasswordPending] = useState(false);
  const [passwordSaved, setPasswordSaved] = useState(false);

  async function onProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProfilePending(true);
    setProfileError(null);
    setProfileSaved(false);
    try {
      const next = await updateProfile({ email, first_name: firstName, last_name: lastName });
      onUser(next);
      setProfileSaved(true);
    } catch (caught) {
      setProfileError(caught);
    } finally {
      setProfilePending(false);
    }
  }

  async function onPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPasswordPending(true);
    setPasswordError(null);
    setPasswordSaved(false);
    try {
      await changePassword({
        current_password: currentPassword,
        password,
        password_confirm: passwordConfirm,
      });
      setCurrentPassword("");
      setPassword("");
      setPasswordConfirm("");
      setPasswordSaved(true);
    } catch (caught) {
      setPasswordError(caught);
    } finally {
      setPasswordPending(false);
    }
  }

  const profileFormError =
    profileError instanceof ApiError && Object.keys(profileError.fields).length === 0
      ? profileError.message
      : null;
  const displayName = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;

  return (
    <article className="mx-auto flex w-full max-w-5xl flex-col gap-8">
      <PageIntro
        icon={UserRound}
        eyebrow={displayName}
        title="Profil"
        description={`Angemeldet als ${user.username}`}
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <form className={`${panelClass} flex flex-col gap-5`} onSubmit={onProfile}>
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <Icon icon={Mail} className="size-5 text-accent" />
            Angaben
          </h2>
          <FormError>{profileFormError}</FormError>
          {profileSaved ? (
            <FormStatus>
              <Icon icon={Check} />
              Gespeichert.
            </FormStatus>
          ) : null}
          <TextField
            label="E-Mail"
            name="email"
            type="email"
            autoComplete="email"
            icon={Mail}
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            error={fieldMessage(profileError, "email")}
          />
          <TextField
            label="Vorname"
            name="first_name"
            autoComplete="given-name"
            value={firstName}
            onChange={(event) => setFirstName(event.target.value)}
            error={fieldMessage(profileError, "first_name")}
          />
          <TextField
            label="Nachname"
            name="last_name"
            autoComplete="family-name"
            value={lastName}
            onChange={(event) => setLastName(event.target.value)}
            error={fieldMessage(profileError, "last_name")}
          />
          <SubmitButton pending={profilePending}>Speichern</SubmitButton>
        </form>
        <form className={`${panelClass} flex flex-col gap-5`} onSubmit={onPassword}>
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <Icon icon={KeyRound} className="size-5 text-accent" />
            Passwort ändern
          </h2>
          <FormError>
            {passwordError instanceof ApiError && Object.keys(passwordError.fields).length === 0
              ? passwordError.message
              : null}
          </FormError>
          {passwordSaved ? (
            <FormStatus>
              <Icon icon={Check} />
              Passwort geändert.
            </FormStatus>
          ) : null}
          <TextField
            label="Aktuelles Passwort"
            name="current_password"
            type="password"
            autoComplete="current-password"
            icon={KeyRound}
            required
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
            error={fieldMessage(passwordError, "current_password")}
          />
          <TextField
            label="Neues Passwort"
            name="password"
            type="password"
            autoComplete="new-password"
            icon={KeyRound}
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            error={fieldMessage(passwordError, "password")}
          />
          <TextField
            label="Neues Passwort wiederholen"
            name="password_confirm"
            type="password"
            autoComplete="new-password"
            icon={KeyRound}
            required
            value={passwordConfirm}
            onChange={(event) => setPasswordConfirm(event.target.value)}
            error={fieldMessage(passwordError, "password_confirm")}
          />
          <SubmitButton pending={passwordPending}>Passwort speichern</SubmitButton>
          <Link href="/passwort-vergessen" className="inline-flex min-h-11 items-center gap-2 text-sm font-medium text-foreground hover:text-accent">
            <Icon icon={Mail} />
            Passwort per E-Mail zurücksetzen
          </Link>
        </form>
      </div>
    </article>
  );
}
