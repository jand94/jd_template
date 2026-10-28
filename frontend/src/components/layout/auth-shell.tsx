import Link from "next/link";
import type { ReactNode } from "react";
import { Layers } from "lucide-react";
import { Icon } from "@/components/ui/icon";
import { buttonPrimary, focusRing, pressable } from "@/components/ui/styles";
import { brand } from "@/config/brand";
import { SiteMain } from "@/components/layout/site-main";
import { ThemeToggle } from "@/components/layout/theme-toggle";

type AuthShellProps = {
  children: ReactNode;
};

export function AuthShell({ children }: AuthShellProps) {
  return (
    <>
      <a
        href="#main"
        className={`fixed top-4 left-4 z-50 -translate-y-24 ${buttonPrimary} focus:translate-y-0`}
      >
        Zum Inhalt springen
      </a>
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 pt-[env(safe-area-inset-top)] backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-3 px-4 sm:px-6 lg:px-8">
          <Link
            href="/anmelden"
            className={`${pressable} ${focusRing} inline-flex h-11 min-w-0 items-center gap-2 rounded-lg pr-2 pl-1 text-base font-semibold tracking-tight text-foreground`}
          >
            <span className="inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent">
              <Icon icon={Layers} />
            </span>
            <span className="truncate">{brand.projectName}</span>
          </Link>
          <div className="ml-auto">
            <ThemeToggle />
          </div>
        </div>
      </header>
      <SiteMain>{children}</SiteMain>
      <footer className="mt-auto border-t border-border pb-[env(safe-area-inset-bottom)]">
        <p className="mx-auto max-w-6xl px-4 py-4 text-sm text-muted-foreground sm:px-6 lg:px-8">
          © {brand.projectName}
        </p>
      </footer>
    </>
  );
}
