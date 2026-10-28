"use client";

import { useEffect } from "react";
import { StatusScreen } from "@/components/ui/status-screen";
import { buttonPrimary } from "@/components/ui/styles";

type ErrorPageProps = {
  error: Error & { digest?: string };
  reset?: () => void;
  unstable_retry?: () => void;
};

export default function AppError({ error, reset, unstable_retry }: ErrorPageProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  const retry = unstable_retry ?? reset;

  return (
    <StatusScreen
      code="Fehler"
      title="Etwas ist schiefgelaufen"
      description="Die Seite konnte nicht angezeigt werden. Der Versuch lässt sich wiederholen."
      action={
        retry ? (
          <button type="button" className={buttonPrimary} onClick={() => retry()}>
            Erneut versuchen
          </button>
        ) : null
      }
    />
  );
}
