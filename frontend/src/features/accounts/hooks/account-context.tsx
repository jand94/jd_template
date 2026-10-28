"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { currentUser, logout as logoutRequest, type Account } from "@/features/accounts/api/session";

async function readCurrentUser(): Promise<Account | null> {
  try {
    return await currentUser();
  } catch {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return currentUser();
  }
}

type AccountStatus = "loading" | "anonymous" | "authenticated";

type AccountContextValue = {
  status: AccountStatus;
  user: Account | null;
  setUser: (user: Account | null) => void;
  logout: () => Promise<void>;
};

const AccountContext = createContext<AccountContextValue | null>(null);

export function AccountProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AccountStatus>("loading");
  const [user, setUserState] = useState<Account | null>(null);

  useEffect(() => {
    let cancelled = false;
    readCurrentUser()
      .then((next) => {
        if (cancelled) {
          return;
        }
        setUserState(next);
        setStatus(next ? "authenticated" : "anonymous");
      })
      .catch(() => {
        // Sitzung bleibt unbestätigt. Geschützte Seiten rendern weiter, solange das Cookie gilt.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo<AccountContextValue>(
    () => ({
      status,
      user,
      setUser(next) {
        setUserState(next);
        setStatus(next ? "authenticated" : "anonymous");
      },
      async logout() {
        await logoutRequest();
        setUserState(null);
        setStatus("anonymous");
      },
    }),
    [status, user],
  );

  return <AccountContext.Provider value={value}>{children}</AccountContext.Provider>;
}

export function useAccount() {
  const value = useContext(AccountContext);
  if (!value) {
    throw new Error("useAccount braucht den AccountProvider.");
  }
  return value;
}
