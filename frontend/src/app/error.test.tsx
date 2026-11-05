import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import AppError from "@/app/error";

describe("AppError", () => {
  afterEach(() => {
    cleanup();
  });

  it("wiederholt den Versuch", () => {
    const retry = vi.fn();
    render(<AppError error={new Error("kaputt")} reset={retry} />);
    fireEvent.click(screen.getByRole("button", { name: "Erneut versuchen" }));
    expect(retry).toHaveBeenCalledOnce();
  });
});
