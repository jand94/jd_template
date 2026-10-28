"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAccount } from "@/features/accounts/hooks/account-context";

export function RequireAccount({ children }: { children: ReactNode }) {
  const account = useAccount();
  const router = useRouter();

  useEffect(() => {
    if (account.status === "anonymous") {
      router.replace("/anmelden");
    }
  }, [account.status, router]);

  if (account.status === "anonymous") {
    return <p className="text-sm text-muted-foreground">Weiter zur Anmeldung.</p>;
  }

  return children;
}

export function RedirectIfAuthenticated({ children }: { children: ReactNode }) {
  const account = useAccount();
  const router = useRouter();

  useEffect(() => {
    if (account.status === "authenticated") {
      router.replace("/dashboard");
    }
  }, [account.status, router]);

  if (account.status === "authenticated") {
    return <p className="text-sm text-muted-foreground">Weiter zum Dashboard.</p>;
  }

  return children;
}
