"use client";

import Link from "next/link";
import { LogIn, LogOut, UserPlus, UserRound } from "lucide-react";
import { useState } from "react";
import { Icon } from "@/components/ui/icon";
import { focusRing, pressable } from "@/components/ui/styles";
import { useAccount } from "@/features/accounts/hooks/account-context";

const itemClass = `flex min-h-11 w-full items-center gap-3 rounded-lg border-l-2 border-transparent px-4 text-base font-medium text-muted-foreground hover:bg-muted hover:text-foreground ${pressable} ${focusRing}`;

export function AccountLinks() {
  const account = useAccount();
  const [pending, setPending] = useState(false);

  if (account.status === "loading") {
    return null;
  }

  async function onLogout() {
    setPending(true);
    try {
      await account.logout();
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mt-2 border-t border-border px-2 pt-2">
      <p className="px-4 py-2 text-xs font-medium tracking-wide text-muted-foreground uppercase">Konto</p>
      <ul className="flex flex-col">
        {account.user ? (
          <>
            <li>
              <Link href="/profil" className={itemClass}>
                <Icon icon={UserRound} className="size-5" />
                Profil
              </Link>
            </li>
            <li>
              <button type="button" className={`${itemClass} text-danger`} disabled={pending} onClick={onLogout}>
                <Icon icon={LogOut} className="size-5" />
                {pending ? "Wird abgemeldet" : "Abmelden"}
              </button>
            </li>
          </>
        ) : (
          <>
            <li>
              <Link href="/anmelden" className={itemClass}>
                <Icon icon={LogIn} className="size-5" />
                Anmelden
              </Link>
            </li>
            <li>
              <Link href="/registrieren" className={itemClass}>
                <Icon icon={UserPlus} className="size-5" />
                Registrieren
              </Link>
            </li>
          </>
        )}
      </ul>
    </div>
  );
}
