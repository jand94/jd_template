import { afterEach, describe, expect, it, vi } from "vitest";
import { createApiClient } from "./api";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("createApiClient", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    document.cookie = "csrftoken=; Max-Age=0";
  });

  it("meldet Feldfehler und detail als ApiError", async () => {
    document.cookie = "csrftoken=token";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo) => {
        const url = String(input);
        if (url.endsWith("/csrf")) {
          return new Response(null, { status: 204 });
        }
        return jsonResponse(400, { detail: "Ungültig", email: ["Pflichtfeld"] });
      }),
    );

    const client = createApiClient("/accounts/v1");

    await expect(client.parse(await client.send("/login", "POST", {}))).rejects.toMatchObject({
      message: "Ungültig",
      status: 400,
      fields: { email: ["Pflichtfeld"] },
    });
  });

  it("übersetzt bekannte detail-Texte", async () => {
    document.cookie = "csrftoken=token";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo) => {
        if (String(input).endsWith("/csrf")) {
          return new Response(null, { status: 204 });
        }
        return jsonResponse(401, { detail: "Invalid username or password." });
      }),
    );

    const client = createApiClient("/accounts/v1", {
      detailMessages: {
        "Invalid username or password.": "Benutzername oder Passwort ist falsch.",
      },
    });

    await expect(client.parse(await client.send("/login", "POST", {}))).rejects.toMatchObject({
      message: "Benutzername oder Passwort ist falsch.",
      status: 401,
    });
  });
});
