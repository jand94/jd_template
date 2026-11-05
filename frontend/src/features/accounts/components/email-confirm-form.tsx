"use client";

import Link from "next/link";
import { MailCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { ApiError, confirmEmail, fieldMessage } from "@/features/accounts/api/session";
import { AuthPanel } from "@/features/accounts/components/auth-panel";
import { FormError, FormStatus } from "@/features/accounts/components/fields";

type Phase = "pending" | "saved" | "failed";

export function EmailConfirmForm({ uid, token }: { uid: string; token: string }) {
  const [phase, setPhase] = useState<Phase>(uid && token ? "pending" : "failed");
  const [error, setError] = useState<unknown>(uid && token ? null : new Error("incomplete"));

  useEffect(() => {
    if (!uid || !token) {
      return;
    }
    let cancelled = false;

    async function confirm() {
      try {
        await confirmEmail({ uid, token });
        if (!cancelled) {
          setPhase("saved");
        }
      } catch (caught) {
        if (!cancelled) {
          setError(caught);
          setPhase("failed");
        }
      }
    }

    void confirm();
    return () => {
      cancelled = true;
    };
  }, [uid, token]);

  return (
    <AuthPanel
      icon={MailCheck}
      title="E-Mail bestätigen"
      description="Der Link aus der Mail schließt die Bestätigung ab."
      footer={
        <Link
          href="/profil"
          className="inline-flex min-h-11 items-center text-sm font-medium text-foreground hover:text-accent"
        >
          Zum Profil
        </Link>
      }
    >
      {phase === "pending" ? <FormStatus>Die Bestätigung läuft.</FormStatus> : null}
      {phase === "saved" ? <FormStatus>Die E-Mail-Adresse ist bestätigt.</FormStatus> : null}
      {phase === "failed" ? (
        <FormError>
          {error instanceof ApiError
            ? (fieldMessage(error, "token") ?? error.message)
            : "Der Link ist unvollständig."}
        </FormError>
      ) : null}
    </AuthPanel>
  );
}
