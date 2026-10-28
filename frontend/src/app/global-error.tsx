"use client";

import { useEffect } from "react";
import "./globals.css";

type GlobalErrorProps = {
  error: Error & { digest?: string };
  reset?: () => void;
  unstable_retry?: () => void;
};

export default function GlobalError({ error, reset, unstable_retry }: GlobalErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  const retry = unstable_retry ?? reset;

  return (
    <html lang="de">
      <body className="flex min-h-full flex-col bg-background font-sans text-foreground">
        <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col justify-center px-4 py-16">
          <p className="text-sm font-medium text-accent">Fehler</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">
            Die Anwendung ist nicht erreichbar
          </h1>
          <p className="mt-3 max-w-xl text-base leading-7 text-muted-foreground">
            Beim Laden der Seite ist ein Fehler aufgetreten.
          </p>
          {retry ? (
            <button
              type="button"
              className="mt-8 inline-flex h-11 items-center justify-center rounded-lg bg-foreground px-4 text-sm font-medium text-background"
              onClick={() => retry()}
            >
              Erneut versuchen
            </button>
          ) : null}
        </main>
      </body>
    </html>
  );
}
