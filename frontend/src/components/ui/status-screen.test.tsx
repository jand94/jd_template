import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { StatusScreen } from "@/components/ui/status-screen";

describe("StatusScreen", () => {
  afterEach(() => {
    cleanup();
  });

  it("zeigt den Titel", () => {
    render(
      <StatusScreen
        code="404"
        title="Diese Seite gibt es nicht"
        description="Die Adresse führt auf keine Seite."
      />,
    );
    expect(screen.getByRole("heading", { name: "Diese Seite gibt es nicht" })).toBeTruthy();
  });
});
