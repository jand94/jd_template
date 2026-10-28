"use client";

import Link from "next/link";
import { Calendar, Check, ImagePlus, KeyRound, Mail, MapPin, Phone, UserRound } from "lucide-react";
import { useEffect, useId, useRef, useState, type FormEvent, type ReactNode } from "react";
import { Icon } from "@/components/ui/icon";
import { buttonSecondary, panelClass } from "@/components/ui/styles";
import {
  ApiError,
  changePassword,
  fieldMessage,
  removeAvatar,
  updateProfile,
  uploadAvatar,
  type Account,
  type ProfileInput,
} from "@/features/accounts/api/session";
import { AccountAvatar } from "@/features/accounts/components/account-avatar";
import { FormError, FormStatus, SelectField, SubmitButton, TextArea, TextField } from "@/features/accounts/components/fields";
import { useAccount } from "@/features/accounts/hooks/account-context";
import { accountDisplayName, mediaUrl } from "@/features/accounts/profile";

const MAX_AVATAR_BYTES = 2 * 1024 * 1024;

const salutationOptions = [
  { value: "", label: "Keine Angabe" },
  { value: "mr", label: "Herr" },
  { value: "ms", label: "Frau" },
  { value: "mx", label: "Mx." },
  { value: "unspecified", label: "Unbestimmt" },
];

const genderOptions = [
  { value: "", label: "Keine Angabe" },
  { value: "female", label: "Weiblich" },
  { value: "male", label: "Männlich" },
  { value: "diverse", label: "Divers" },
  { value: "undisclosed", label: "Keine Angabe machen" },
];

type Draft = Omit<ProfileInput, "date_of_birth"> & { date_of_birth: string };

export function ProfileScreen() {
  const account = useAccount();

  if (!account.user) {
    return null;
  }

  return <ProfileForms key={account.user.id} user={account.user} onUser={account.setUser} />;
}

function ProfileForms({ user, onUser }: { user: Account; onUser: (user: Account) => void }) {
  const fileId = useId();
  const fileInput = useRef<HTMLInputElement>(null);
  const avatarRequest = useRef(0);
  const [draft, setDraft] = useState<Draft>(() => draftFrom(user));
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [removeImage, setRemoveImage] = useState(false);
  const [avatarError, setAvatarError] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<unknown>(null);
  const [profilePending, setProfilePending] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [passwordError, setPasswordError] = useState<unknown>(null);
  const [passwordPending, setPasswordPending] = useState(false);
  const [passwordSaved, setPasswordSaved] = useState(false);

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  function setField<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function chooseAvatar(next: File | null) {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    const message = next ? avatarFileMessage(next) : null;
    setAvatarError(message);
    setFile(message ? null : next);
    setPreview(next && !message ? URL.createObjectURL(next) : null);
    setRemoveImage(false);
    if (!next && fileInput.current) {
      fileInput.current.value = "";
    }
    return message;
  }

  async function storeAvatar(next: File) {
    const requestId = ++avatarRequest.current;
    setProfilePending(true);
    setProfileError(null);
    setProfileSaved(false);
    try {
      const current = await uploadAvatar(next);
      if (requestId !== avatarRequest.current) {
        return;
      }
      onUser(current);
      chooseAvatar(null);
      setProfileSaved(true);
    } catch (caught) {
      if (requestId !== avatarRequest.current) {
        return;
      }
      setProfileError(caught);
    } finally {
      if (requestId === avatarRequest.current) {
        setProfilePending(false);
      }
    }
  }

  async function clearAvatar() {
    const requestId = ++avatarRequest.current;
    chooseAvatar(null);
    setRemoveImage(true);
    if (!user.avatar) {
      return;
    }
    setProfilePending(true);
    setProfileError(null);
    setProfileSaved(false);
    try {
      const current = await removeAvatar();
      if (requestId !== avatarRequest.current) {
        return;
      }
      onUser(current);
      setRemoveImage(false);
      setProfileSaved(true);
    } catch (caught) {
      if (requestId !== avatarRequest.current) {
        return;
      }
      setProfileError(caught);
    } finally {
      if (requestId === avatarRequest.current) {
        setProfilePending(false);
      }
    }
  }

  async function onProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (file && avatarFileMessage(file)) {
      setAvatarError(avatarFileMessage(file));
      return;
    }
    setProfilePending(true);
    setProfileError(null);
    setProfileSaved(false);
    try {
      let current = await updateProfile({
        ...draft,
        date_of_birth: draft.date_of_birth || null,
      });
      onUser(current);
      if (file) {
        current = await uploadAvatar(file);
        onUser(current);
      } else if (removeImage && user.avatar) {
        current = await removeAvatar();
        onUser(current);
      }
      chooseAvatar(null);
      setRemoveImage(false);
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
  const displayName = accountDisplayName(user);
  const shownAvatar = preview ?? (removeImage ? null : mediaUrl(user.avatar));
  const avatarUser = { ...user, avatar: shownAvatar };

  return (
    <article className="mx-auto grid w-full max-w-5xl gap-4 lg:grid-cols-[18rem_1fr]">
      <form className="grid gap-4 lg:col-span-2 lg:grid-cols-[18rem_1fr]" onSubmit={onProfile}>
        <aside className={`${panelClass} flex flex-col gap-5 lg:self-start`}>
          <AccountAvatar
            user={avatarUser}
            alt={shownAvatar ? `Avatar von ${user.username}` : ""}
            className="size-24 text-2xl"
          />
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-balance">{displayName}</h1>
            <p className="mt-1 text-sm text-muted-foreground">@{user.username}</p>
          </div>
          <dl className="flex flex-col gap-2 text-sm">
            <StatusItem term="E-Mail" value={user.is_email_verified ? "Bestätigt" : "Nicht bestätigt"} />
            <StatusItem term="Telefon" value={user.is_phone_verified ? "Bestätigt" : "Nicht bestätigt"} />
            <StatusItem term="Alter" value={user.age === null ? "—" : String(user.age)} />
            <StatusItem term="Dabei seit" value={formatDate(user.date_joined)} />
          </dl>
          <div className="flex flex-col gap-2">
            <label htmlFor={fileId} className={`${buttonSecondary} cursor-pointer`}>
              <Icon icon={ImagePlus} />
              Bild wählen
            </label>
            <input
              ref={fileInput}
              id={fileId}
              name="avatar"
              type="file"
              accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
              className="sr-only"
              disabled={profilePending}
              onChange={(event) => {
                const next = event.target.files?.[0] ?? null;
                const message = chooseAvatar(next);
                if (next && !message) {
                  void storeAvatar(next);
                }
              }}
            />
            {user.avatar || preview ? (
              <button
                type="button"
                className="inline-flex min-h-11 items-center text-sm font-medium text-danger"
                onClick={() => {
                  void clearAvatar();
                }}
              >
                Bild entfernen
              </button>
            ) : null}
            <p className="text-sm text-muted-foreground">JPEG, PNG oder WebP, höchstens 2 MB.</p>
            {avatarError ? <p className="text-sm text-danger">{avatarError}</p> : null}
            {fieldMessage(profileError, "avatar") ? (
              <p className="text-sm text-danger">{fieldMessage(profileError, "avatar")}</p>
            ) : null}
            {profileFormError ? <p className="text-sm text-danger">{profileFormError}</p> : null}
          </div>
        </aside>
        <div className="flex flex-col gap-4">
          <FormError>{profileFormError}</FormError>
          {profileSaved ? (
            <FormStatus>
              <Icon icon={Check} />
              Gespeichert.
            </FormStatus>
          ) : null}
          <Section icon={UserRound} title="Persönliches">
            <div className="grid gap-5 sm:grid-cols-2">
              <SelectField
                label="Anrede"
                name="salutation"
                value={draft.salutation}
                onChange={(value) => setField("salutation", value)}
                options={salutationOptions}
                error={fieldMessage(profileError, "salutation")}
              />
              <TextField
                label="Titel"
                name="title"
                autoComplete="honorific-prefix"
                value={draft.title}
                onChange={(event) => setField("title", event.target.value)}
                error={fieldMessage(profileError, "title")}
              />
              <TextField
                label="Vorname"
                name="first_name"
                autoComplete="given-name"
                value={draft.first_name}
                onChange={(event) => setField("first_name", event.target.value)}
                error={fieldMessage(profileError, "first_name")}
              />
              <TextField
                label="Zweiter Vorname"
                name="middle_name"
                autoComplete="additional-name"
                value={draft.middle_name}
                onChange={(event) => setField("middle_name", event.target.value)}
                error={fieldMessage(profileError, "middle_name")}
              />
              <TextField
                label="Nachname"
                name="last_name"
                autoComplete="family-name"
                value={draft.last_name}
                onChange={(event) => setField("last_name", event.target.value)}
                error={fieldMessage(profileError, "last_name")}
              />
              <TextField
                label="Bevorzugter Name"
                name="preferred_name"
                autoComplete="nickname"
                value={draft.preferred_name}
                onChange={(event) => setField("preferred_name", event.target.value)}
                error={fieldMessage(profileError, "preferred_name")}
              />
              <SelectField
                label="Geschlecht"
                name="gender"
                value={draft.gender}
                onChange={(value) => setField("gender", value)}
                options={genderOptions}
                error={fieldMessage(profileError, "gender")}
              />
              <TextField
                label="Pronomen"
                name="pronouns"
                value={draft.pronouns}
                onChange={(event) => setField("pronouns", event.target.value)}
                error={fieldMessage(profileError, "pronouns")}
              />
              <TextField
                label="Geburtsdatum"
                name="date_of_birth"
                type="date"
                autoComplete="bday"
                value={draft.date_of_birth}
                onChange={(event) => setField("date_of_birth", event.target.value)}
                error={fieldMessage(profileError, "date_of_birth")}
              />
              <TextField
                label="Geburtsort"
                name="place_of_birth"
                value={draft.place_of_birth}
                onChange={(event) => setField("place_of_birth", event.target.value)}
                error={fieldMessage(profileError, "place_of_birth")}
              />
              <TextField
                label="Staatsangehörigkeit"
                name="nationality"
                autoComplete="country"
                hint="Zweistelliger Ländercode, zum Beispiel DE."
                value={draft.nationality}
                onChange={(event) => setField("nationality", event.target.value)}
                error={fieldMessage(profileError, "nationality")}
              />
            </div>
          </Section>
          <Section icon={Phone} title="Kontakt">
            <div className="grid gap-5 sm:grid-cols-2">
              <TextField
                label="E-Mail"
                name="email"
                type="email"
                autoComplete="email"
                icon={Mail}
                required
                value={draft.email}
                onChange={(event) => setField("email", event.target.value)}
                error={fieldMessage(profileError, "email")}
              />
              <TextField
                label="Telefon"
                name="phone"
                type="tel"
                autoComplete="tel"
                value={draft.phone}
                onChange={(event) => setField("phone", event.target.value)}
                error={fieldMessage(profileError, "phone")}
              />
              <TextField
                label="Mobil"
                name="mobile"
                type="tel"
                autoComplete="tel"
                value={draft.mobile}
                onChange={(event) => setField("mobile", event.target.value)}
                error={fieldMessage(profileError, "mobile")}
              />
              <TextField
                label="Website"
                name="website"
                type="url"
                autoComplete="url"
                value={draft.website}
                onChange={(event) => setField("website", event.target.value)}
                error={fieldMessage(profileError, "website")}
              />
              <TextField
                label="Sprache"
                name="language"
                hint="Zum Beispiel de oder en-us."
                value={draft.language}
                onChange={(event) => setField("language", event.target.value)}
                error={fieldMessage(profileError, "language")}
              />
              <TextField
                label="Zeitzone"
                name="timezone"
                hint="Zum Beispiel Europe/Berlin."
                value={draft.timezone}
                onChange={(event) => setField("timezone", event.target.value)}
                error={fieldMessage(profileError, "timezone")}
              />
            </div>
          </Section>
          <Section icon={MapPin} title="Adresse">
            <div className="grid gap-5 sm:grid-cols-2">
              <TextField
                label="Straße"
                name="street"
                autoComplete="address-line1"
                value={draft.street}
                onChange={(event) => setField("street", event.target.value)}
                error={fieldMessage(profileError, "street")}
              />
              <TextField
                label="Hausnummer"
                name="house_number"
                value={draft.house_number}
                onChange={(event) => setField("house_number", event.target.value)}
                error={fieldMessage(profileError, "house_number")}
              />
              <TextField
                label="Adresszusatz"
                name="address_line2"
                autoComplete="address-line2"
                value={draft.address_line2}
                onChange={(event) => setField("address_line2", event.target.value)}
                error={fieldMessage(profileError, "address_line2")}
              />
              <TextField
                label="Postleitzahl"
                name="postal_code"
                autoComplete="postal-code"
                value={draft.postal_code}
                onChange={(event) => setField("postal_code", event.target.value)}
                error={fieldMessage(profileError, "postal_code")}
              />
              <TextField
                label="Ort"
                name="city"
                autoComplete="address-level2"
                value={draft.city}
                onChange={(event) => setField("city", event.target.value)}
                error={fieldMessage(profileError, "city")}
              />
              <TextField
                label="Region"
                name="region"
                autoComplete="address-level1"
                value={draft.region}
                onChange={(event) => setField("region", event.target.value)}
                error={fieldMessage(profileError, "region")}
              />
              <TextField
                label="Land"
                name="country"
                autoComplete="country"
                hint="Zweistelliger Ländercode, zum Beispiel DE."
                value={draft.country}
                onChange={(event) => setField("country", event.target.value)}
                error={fieldMessage(profileError, "country")}
              />
            </div>
          </Section>
          <Section icon={Calendar} title="Über mich">
            <TextArea
              label="Kurztext"
              name="bio"
              value={draft.bio}
              onChange={(value) => setField("bio", value)}
              error={fieldMessage(profileError, "bio")}
            />
            <SubmitButton pending={profilePending}>Speichern</SubmitButton>
          </Section>
        </div>
      </form>
      <form className={`${panelClass} flex flex-col gap-5 lg:col-start-2`} onSubmit={onPassword}>
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
    </article>
  );
}

function Section({ icon, title, children }: { icon: typeof UserRound; title: string; children: ReactNode }) {
  return (
    <section className={`${panelClass} flex flex-col gap-5`}>
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <Icon icon={icon} className="size-5 text-accent" />
        {title}
      </h2>
      {children}
    </section>
  );
}

function StatusItem({ term, value }: { term: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-muted-foreground">{term}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}

function draftFrom(user: Account): Draft {
  return {
    email: user.email,
    salutation: user.salutation,
    title: user.title,
    first_name: user.first_name,
    middle_name: user.middle_name,
    last_name: user.last_name,
    preferred_name: user.preferred_name,
    gender: user.gender,
    pronouns: user.pronouns,
    date_of_birth: user.date_of_birth ?? "",
    place_of_birth: user.place_of_birth,
    nationality: user.nationality,
    phone: user.phone,
    mobile: user.mobile,
    website: user.website,
    street: user.street,
    house_number: user.house_number,
    address_line2: user.address_line2,
    postal_code: user.postal_code,
    city: user.city,
    region: user.region,
    country: user.country,
    bio: user.bio,
    language: user.language,
    timezone: user.timezone,
  };
}

function avatarFileMessage(file: File): string | null {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const allowedExtension = extension === "jpg" || extension === "jpeg" || extension === "png" || extension === "webp";
  const allowedType =
    file.type === "image/jpeg" ||
    file.type === "image/jpg" ||
    file.type === "image/pjpeg" ||
    file.type === "image/png" ||
    file.type === "image/x-png" ||
    file.type === "image/webp";
  if ((!file.type && !allowedExtension) || (file.type && !allowedType && !allowedExtension)) {
    return "Bitte ein JPEG-, PNG- oder WebP-Bild wählen.";
  }
  if (file.size > MAX_AVATAR_BYTES) {
    return "Das Bild darf höchstens 2 MB groß sein.";
  }
  return null;
}

function formatDate(value: string | null): string {
  if (!value) {
    return "—";
  }
  const [date] = value.split("T");
  const [year, month, day] = date.split("-");
  if (!year || !month || !day) {
    return value;
  }
  return `${day}.${month}.${year}`;
}
