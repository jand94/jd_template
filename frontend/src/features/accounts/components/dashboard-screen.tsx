"use client";

import Link from "next/link";
import { ArrowRight, LayoutDashboard, Server, UserRound } from "lucide-react";
import { Icon } from "@/components/ui/icon";
import { PageIntro } from "@/components/ui/page-intro";
import { focusRing, panelClass, pressable } from "@/components/ui/styles";
import { brand } from "@/config/brand";
import { useAccount } from "@/features/accounts/hooks/account-context";

const cardLink = `${panelClass} flex flex-col ${pressable} ${focusRing} hover:bg-muted`;

export function DashboardScreen() {
  const account = useAccount();
  const user = account.user;
  if (!user) {
    return null;
  }

  const name = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;

  return (
    <article className="flex flex-col gap-10">
      <PageIntro
        icon={LayoutDashboard}
        eyebrow={brand.projectName}
        title="Dashboard"
        description={`Willkommen, ${name}.`}
      />
      <ul className="grid gap-4 lg:grid-cols-3">
        <li>
          <Link href="/profil" className={cardLink}>
            <span className="inline-flex size-10 items-center justify-center rounded-lg bg-accent-soft text-accent">
              <Icon icon={UserRound} className="size-5" />
            </span>
            <h2 className="mt-4 text-lg font-semibold tracking-tight">Profil</h2>
            <p className="mt-2 text-sm leading-6 break-words text-muted-foreground">{user.email}</p>
            <p className="mt-4 inline-flex items-center gap-2 text-sm font-medium">
              Profil öffnen
              <Icon icon={ArrowRight} />
            </p>
          </Link>
        </li>
        <li>
          <Link href="/system" className={cardLink}>
            <span className="inline-flex size-10 items-center justify-center rounded-lg bg-accent-soft text-accent">
              <Icon icon={Server} className="size-5" />
            </span>
            <h2 className="mt-4 text-lg font-semibold tracking-tight">System</h2>
            <p className="mt-2 text-sm leading-6 break-words text-muted-foreground">
              {brand.apiTitle} · {brand.apiVersion}
            </p>
            <p className="mt-4 inline-flex items-center gap-2 text-sm font-medium">
              System ansehen
              <Icon icon={ArrowRight} />
            </p>
          </Link>
        </li>
        <li className={panelClass}>
          <h2 className="text-sm text-muted-foreground">Angemeldet als</h2>
          <p className="mt-2 text-lg font-semibold tracking-tight break-words">{user.username}</p>
          <p className="mt-3 text-sm leading-6 text-pretty text-muted-foreground">{brand.apiDescription}</p>
        </li>
      </ul>
    </article>
  );
}
