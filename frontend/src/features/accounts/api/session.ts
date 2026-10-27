export type Account = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
};

export class ApiError extends Error {
  readonly status: number;
  readonly fields: Record<string, string[]>;

  constructor(message: string, status: number, fields: Record<string, string[]> = {}) {
    super(message);
    this.status = status;
    this.fields = fields;
  }
}

const detailMessages: Record<string, string> = {
  "Invalid username or password.": "Benutzername oder Passwort ist falsch.",
};

function readCookie(name: string): string | null {
  const prefix = `${name}=`;
  for (const part of document.cookie.split(";")) {
    const cookie = part.trim();
    if (cookie.startsWith(prefix)) {
      return decodeURIComponent(cookie.slice(prefix.length));
    }
  }
  return null;
}

async function refreshCsrf(): Promise<string> {
  const response = await fetch("/accounts/v1/csrf", {
    credentials: "same-origin",
    cache: "no-store",
  });
  if (!response.ok && response.status !== 204) {
    throw new ApiError("Die Sitzung konnte nicht vorbereitet werden.", response.status);
  }
  const token = readCookie("csrftoken");
  if (!token) {
    throw new ApiError("Die Sitzung konnte nicht vorbereitet werden.", response.status);
  }
  return token;
}

function readFields(data: unknown): Record<string, string[]> {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return {};
  }

  const fields: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(data)) {
    if (key === "detail") {
      continue;
    }
    if (typeof value === "string") {
      fields[key] = [value];
    } else if (Array.isArray(value)) {
      fields[key] = value.map(String);
    }
  }
  return fields;
}

async function parse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }

  const data: unknown = await response.json().catch(() => null);
  if (response.ok) {
    return data as T;
  }

  const fields = readFields(data);
  const detail =
    data && typeof data === "object" && "detail" in data && typeof data.detail === "string"
      ? data.detail
      : "";
  const message =
    detailMessages[detail] ||
    detail ||
    (response.status === 403
      ? "Die Anfrage wurde abgelehnt. Bitte erneut versuchen."
      : "Die Anfrage ist fehlgeschlagen.");
  throw new ApiError(message, response.status, fields);
}

async function send(path: string, method: string, body?: unknown): Promise<Response> {
  const headers = new Headers({ Accept: "application/json" });
  if (body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  if (method !== "GET" && method !== "HEAD") {
    headers.set("X-CSRFToken", await refreshCsrf());
  }

  return fetch(`/accounts/v1${path}`, {
    method,
    credentials: "same-origin",
    cache: "no-store",
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export async function currentUser(): Promise<Account | null> {
  const response = await fetch("/accounts/v1/me", {
    credentials: "same-origin",
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (response.status === 401 || response.status === 403) {
    return null;
  }
  if (!response.ok) {
    return null;
  }
  return (await response.json()) as Account;
}

export async function login(username: string, password: string): Promise<Account> {
  const response = await send("/login", "POST", { username, password });
  return parse<Account>(response);
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
  const response = await send("/register", "POST", input);
  return parse<Account>(response);
}

export async function logout(): Promise<void> {
  const response = await send("/logout", "POST");
  await parse<void>(response);
}

export async function updateProfile(input: {
  email: string;
  first_name: string;
  last_name: string;
}): Promise<Account> {
  const response = await send("/me", "PATCH", input);
  return parse<Account>(response);
}

export async function changePassword(input: {
  current_password: string;
  password: string;
  password_confirm: string;
}): Promise<void> {
  const response = await send("/password/change", "POST", input);
  await parse<void>(response);
}

export async function requestPasswordReset(email: string): Promise<void> {
  const response = await send("/password/reset", "POST", { email });
  await parse<void>(response);
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
  return message;
}
