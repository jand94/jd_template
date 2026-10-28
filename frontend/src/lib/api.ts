export class ApiError extends Error {
  readonly status: number;
  readonly fields: Record<string, string[]>;

  constructor(message: string, status: number, fields: Record<string, string[]> = {}) {
    super(message);
    this.status = status;
    this.fields = fields;
  }
}

type ClientOptions = {
  csrfPath?: string;
  detailMessages?: Record<string, string>;
};

const defaultCsrfPath = "/accounts/v1/csrf";

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

export function createApiClient(basePath: string, options: ClientOptions = {}) {
  const csrfPath = options.csrfPath ?? defaultCsrfPath;
  const detailMessages = options.detailMessages ?? {};

  function url(path: string): string {
    if (!path || path === "/") {
      return basePath;
    }
    return `${basePath}${path.startsWith("/") ? path : `/${path}`}`;
  }

  async function refreshCsrf(): Promise<string> {
    const response = await fetch(csrfPath, {
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

  async function send(path: string, method: string, body?: unknown): Promise<Response> {
    const headers = new Headers({ Accept: "application/json" });
    if (body !== undefined) {
      headers.set("Content-Type", "application/json");
    }
    if (method !== "GET" && method !== "HEAD") {
      headers.set("X-CSRFToken", await refreshCsrf());
    }

    return fetch(url(path), {
      method,
      credentials: "same-origin",
      cache: "no-store",
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  }

  async function sendForm(path: string, body: FormData, method = "POST"): Promise<Response> {
    return fetch(url(path), {
      method,
      credentials: "same-origin",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        "X-CSRFToken": await refreshCsrf(),
      },
      body,
    });
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

  return { send, sendForm, parse };
}
