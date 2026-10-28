"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Layers, LayoutDashboard, Menu, Server, X, type LucideIcon } from "lucide-react";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Icon } from "@/components/ui/icon";
import { focusRing, pressable } from "@/components/ui/styles";
import { isCurrentPath, type NavigationItem } from "@/config/navigation";
import { ThemeToggle } from "@/components/layout/theme-toggle";

const itemIcons: Record<string, LucideIcon> = {
  "/dashboard": LayoutDashboard,
  "/system": Server,
};

const control = `${pressable} ${focusRing}`;

type SiteHeaderProps = {
  projectName: string;
  items: NavigationItem[];
  accountMenu: ReactNode;
  mobileAccount: ReactNode;
};

export function SiteHeader({ projectName, items, accountMenu, mobileAccount }: SiteHeaderProps) {
  const pathname = usePathname();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const menuId = useId();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) {
      return;
    }

    const onClose = () => setOpen(false);
    dialog.addEventListener("close", onClose);
    return () => dialog.removeEventListener("close", onClose);
  }, []);

  useEffect(() => {
    dialogRef.current?.close();
  }, [pathname]);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)");
    const onChange = () => {
      if (media.matches) {
        dialogRef.current?.close();
      }
    };

    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  function openMenu() {
    const dialog = dialogRef.current;
    if (!dialog || dialog.open) {
      return;
    }

    dialog.showModal();
    setOpen(true);
  }

  function closeMenu() {
    dialogRef.current?.close();
    menuButtonRef.current?.focus();
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 pt-[env(safe-area-inset-top)] backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-2 px-4 sm:gap-4 sm:px-6 lg:px-8">
        <Link
          href="/dashboard"
          className={`${control} inline-flex h-11 min-w-0 items-center gap-2 rounded-lg pr-2 pl-1 text-base font-semibold tracking-tight text-foreground`}
        >
          <span className="inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent">
            <Icon icon={Layers} />
          </span>
          <span className="truncate">{projectName}</span>
        </Link>
        <nav className="hidden min-w-0 md:block" aria-label="Hauptnavigation">
          <ul className="flex items-center gap-1">
            {items.map((item) => {
              const current = isCurrentPath(pathname, item.href);
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    aria-current={current ? "page" : undefined}
                    className={`${control} relative inline-flex h-11 items-center gap-2 rounded-lg px-3 text-sm font-medium ${
                      current
                        ? "text-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    {itemIcons[item.href] ? <Icon icon={itemIcons[item.href]} /> : null}
                    {item.label}
                    {current ? (
                      <span
                        aria-hidden="true"
                        className="absolute inset-x-3 bottom-1.5 h-0.5 bg-foreground"
                      />
                    ) : null}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="ml-auto flex items-center gap-1">
          <ThemeToggle />
          {accountMenu}
          <button
            ref={menuButtonRef}
            type="button"
            className={`${control} inline-flex size-11 items-center justify-center rounded-lg text-foreground hover:bg-muted md:hidden`}
            aria-expanded={open}
            aria-controls={menuId}
            aria-label={open ? "Menü schließen" : "Menü öffnen"}
            onClick={open ? closeMenu : openMenu}
          >
            {open ? <Icon icon={X} className="size-5" /> : <Icon icon={Menu} className="size-5" />}
          </button>
        </div>
      </div>
      <dialog
        ref={dialogRef}
        id={menuId}
        className="nav-dialog"
        aria-label="Menü"
        onClick={(event) => {
          if (event.target === event.currentTarget) {
            event.currentTarget.close();
          }
        }}
      >
        <div className="max-h-[100dvh] overflow-auto border-b border-border bg-background pb-[env(safe-area-inset-bottom)]">
          <div className="flex h-16 items-center justify-between gap-3 px-4 pt-[env(safe-area-inset-top)]">
            <p className="flex min-w-0 items-center gap-2 font-semibold tracking-tight">
              <span className="inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent">
                <Icon icon={Layers} />
              </span>
              <span className="truncate">{projectName}</span>
            </p>
            <button
              type="button"
              className={`${control} inline-flex size-11 items-center justify-center rounded-lg hover:bg-muted`}
              aria-label="Menü schließen"
              onClick={closeMenu}
            >
              <Icon icon={X} className="size-5" />
            </button>
          </div>
          <nav aria-label="Menü">
            <ul className="flex flex-col px-2 pb-3">
              {items.map((item) => {
                const current = isCurrentPath(pathname, item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={current ? "page" : undefined}
                      className={`${control} flex min-h-11 items-center gap-3 rounded-lg border-l-2 px-4 text-base font-medium ${
                        current
                          ? "border-accent bg-muted text-foreground"
                          : "border-transparent text-muted-foreground hover:bg-muted hover:text-foreground"
                      }`}
                      onClick={closeMenu}
                    >
                      {itemIcons[item.href] ? <Icon icon={itemIcons[item.href]} className="size-5" /> : null}
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
          {mobileAccount}
        </div>
      </dialog>
    </header>
  );
}
