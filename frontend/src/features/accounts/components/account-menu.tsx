"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown, CircleUser, LogIn, LogOut, UserPlus, UserRound } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";
import { Icon } from "@/components/ui/icon";
import { focusRing, pressable } from "@/components/ui/styles";
import { AccountAvatar } from "@/features/accounts/components/account-avatar";
import { useAccount } from "@/features/accounts/hooks/account-context";
import { accountDisplayName } from "@/features/accounts/profile";

const itemClass = `flex min-h-11 w-full items-center gap-2 rounded-lg px-3 text-left text-sm font-medium text-foreground hover:bg-muted ${pressable} ${focusRing}`;

export function AccountMenu() {
  const account = useAccount();
  const pathname = usePathname();
  const menuId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [openPath, setOpenPath] = useState<string | null>(null);
  const [pendingLogout, setPendingLogout] = useState(false);
  const open = openPath === pathname;

  useEffect(() => {
    if (!open) {
      return;
    }

    function onPointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpenPath(null);
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpenPath(null);
        buttonRef.current?.focus();
      }
    }

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  async function onLogout() {
    setPendingLogout(true);
    try {
      await account.logout();
      setOpenPath(null);
    } finally {
      setPendingLogout(false);
    }
  }

  if (account.status === "loading") {
    return <span className="inline-flex h-11 w-20" aria-hidden="true" />;
  }

  const label = account.user ? accountDisplayName(account.user) : "Konto";

  return (
    <div ref={rootRef} className="relative">
      <button
        ref={buttonRef}
        type="button"
        className={`inline-flex h-11 max-w-36 items-center gap-2 rounded-lg px-3 text-sm font-medium text-foreground hover:bg-muted sm:max-w-44 ${pressable} ${focusRing}`}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        onClick={() => setOpenPath(open ? null : pathname)}
      >
        {account.user ? (
          <AccountAvatar key={account.user.avatar ?? "none"} user={account.user} className="size-7 shrink-0 text-xs" />
        ) : (
          <Icon icon={CircleUser} className="size-4 shrink-0" />
        )}
        <span className="truncate">{label}</span>
        <Icon
          icon={ChevronDown}
          className={`size-4 shrink-0 transition-transform duration-150 ease-[cubic-bezier(0.23,1,0.32,1)] motion-reduce:transition-none ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open ? (
        <div
          id={menuId}
          role="menu"
          aria-label="Konto"
          className="menu-in absolute top-full right-0 z-50 mt-2 w-56 rounded-xl border border-border bg-card p-1 shadow-[var(--shadow)]"
        >
          {account.user ? (
            <>
              <Link href="/profil" role="menuitem" className={itemClass}>
                <Icon icon={UserRound} />
                Profil
              </Link>
              <button
                type="button"
                role="menuitem"
                className={`${itemClass} text-danger`}
                disabled={pendingLogout}
                onClick={onLogout}
              >
                <Icon icon={LogOut} />
                {pendingLogout ? "Wird abgemeldet" : "Abmelden"}
              </button>
            </>
          ) : (
            <>
              <Link href="/anmelden" role="menuitem" className={itemClass}>
                <Icon icon={LogIn} />
                Anmelden
              </Link>
              <Link href="/registrieren" role="menuitem" className={itemClass}>
                <Icon icon={UserPlus} />
                Registrieren
              </Link>
            </>
          )}
        </div>
      ) : null}
    </div>
  );
}
