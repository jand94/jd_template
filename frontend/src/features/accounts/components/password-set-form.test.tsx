import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PasswordSetForm } from "@/features/accounts/components/password-set-form";

describe("PasswordSetForm", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    document.cookie = "csrftoken=; Max-Age=0";
  });

  it("nennt einen unvollständigen Link", () => {
    render(<PasswordSetForm uid="" token="" />);
    expect(screen.getByText("Der Link ist unvollständig.")).toBeTruthy();
  });

  it("schickt uid und token an die API", async () => {
    document.cookie = "csrftoken=token";
    const calls: { url: string; body?: string }[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        calls.push({
          url: String(input),
          body: typeof init?.body === "string" ? init.body : undefined,
        });
        return new Response(null, { status: 204 });
      }),
    );

    render(<PasswordSetForm uid="abc" token="def" />);
    fireEvent.change(screen.getByLabelText("Neues Passwort"), {
      target: { value: "a-long-password-99" },
    });
    fireEvent.change(screen.getByLabelText("Passwort wiederholen"), {
      target: { value: "a-long-password-99" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Passwort speichern" }));

    expect(await screen.findByText(/Passwort ist gespeichert/)).toBeTruthy();
    const post = calls.find((call) => call.url.endsWith("/password/reset/confirm"));
    expect(JSON.parse(post?.body ?? "{}")).toEqual({
      uid: "abc",
      token: "def",
      password: "a-long-password-99",
      password_confirm: "a-long-password-99",
    });
  });
});
