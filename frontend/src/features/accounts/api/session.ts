import { ApiError, createApiClient } from "@/lib/api";

export { ApiError };

export type Account = {
  id: number;
  username: string;
  email: string;
  salutation: string;
  title: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  preferred_name: string;
  gender: string;
  pronouns: string;
  date_of_birth: string | null;
  place_of_birth: string;
  nationality: string;
  phone: string;
  mobile: string;
  website: string;
  street: string;
  house_number: string;
  address_line2: string;
  postal_code: string;
  city: string;
  region: string;
  country: string;
  bio: string;
  avatar: string | null;
  language: string;
  timezone: string;
  age: number | null;
  is_email_verified: boolean;
  is_phone_verified: boolean;
  email_verified_at: string | null;
  phone_verified_at: string | null;
  terms_accepted_at: string | null;
  date_joined: string;
  last_login: string | null;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
};

export type ProfileInput = {
  email: string;
  salutation: string;
  title: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  preferred_name: string;
  gender: string;
  pronouns: string;
  date_of_birth: string | null;
  place_of_birth: string;
  nationality: string;
  phone: string;
  mobile: string;
  website: string;
  street: string;
  house_number: string;
  address_line2: string;
  postal_code: string;
  city: string;
  region: string;
  country: string;
  bio: string;
  language: string;
  timezone: string;
};

const api = createApiClient("/accounts/v1", {
  detailMessages: {
    "Invalid username or password.": "Benutzername oder Passwort ist falsch.",
  },
});

export async function currentUser(): Promise<Account | null> {
  const response = await api.send("/me", "GET");
  if (response.status === 401 || response.status === 403) {
    return null;
  }
  if (!response.ok) {
    throw new ApiError("Die Sitzung konnte nicht gelesen werden.", response.status);
  }
  return (await response.json()) as Account;
}

export async function login(username: string, password: string): Promise<Account> {
  return api.parse<Account>(await api.send("/login", "POST", { username, password }));
}

export async function register(input: {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  terms_accepted: boolean;
}): Promise<Account> {
  return api.parse<Account>(await api.send("/register", "POST", input));
}

export async function logout(): Promise<void> {
  await api.parse<void>(await api.send("/logout", "POST"));
}

export async function updateProfile(input: ProfileInput): Promise<Account> {
  return api.parse<Account>(await api.send("/me", "PATCH", input));
}

export async function uploadAvatar(file: File): Promise<Account> {
  const body = new FormData();
  body.append("avatar", file);
  return api.parse<Account>(await api.sendForm("/me", body, "PATCH"));
}

export async function removeAvatar(): Promise<Account> {
  return api.parse<Account>(await api.send("/me", "PATCH", { avatar: null }));
}

export async function changePassword(input: {
  current_password: string;
  password: string;
  password_confirm: string;
}): Promise<void> {
  await api.parse<void>(await api.send("/password/change", "POST", input));
}

export async function requestPasswordReset(email: string): Promise<void> {
  await api.parse<void>(await api.send("/password/reset", "POST", { email }));
}

export function fieldMessage(error: unknown, field: string): string | undefined {
  if (!(error instanceof ApiError)) {
    return undefined;
  }
  const message = error.fields[field]?.[0];
  if (!message) {
    return undefined;
  }
  if (message === "The two password fields didn’t match." || message === "The two password fields didn't match.") {
    return "Die Passwörter stimmen nicht überein.";
  }
  if (message === "You must accept the terms.") {
    return "Die Bedingungen müssen akzeptiert werden.";
  }
  if (message === "The current password is incorrect.") {
    return "Das aktuelle Passwort ist falsch.";
  }
  if (message === "A user with that email address already exists.") {
    return "Diese E-Mail wird bereits verwendet.";
  }
  if (message === "Enter a two-letter ISO 3166-1 country code.") {
    return "Bitte einen zweistelligen Ländercode angeben, zum Beispiel DE.";
  }
  if (message === "Enter a phone number with digits, spaces, and an optional leading +.") {
    return "Bitte eine Telefonnummer mit Ziffern, Leerzeichen und optionalem + angeben.";
  }
  if (message.startsWith("Enter a language code")) {
    return "Bitte einen Sprachcode angeben, zum Beispiel de.";
  }
  if (message.startsWith("Enter a valid IANA time zone")) {
    return "Bitte eine Zeitzone angeben, zum Beispiel Europe/Berlin.";
  }
  if (message === "Date of birth cannot be in the future.") {
    return "Das Geburtsdatum darf nicht in der Zukunft liegen.";
  }
  if (message.includes("JPEG") || message.includes("WebP") || message.startsWith("Avatar ")) {
    return "Bitte ein JPEG-, PNG- oder WebP-Bild bis 2 MB hochladen.";
  }
  return message;
}
