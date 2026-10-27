"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { isCurrentPath, type NavigationItem } from "@/config/navigation";
import { ThemeToggle } from "@/components/layout/theme-toggle";

const pressable =
  "cursor-pointer touch-manipulation transition-[color,background-color,transform] duration-150 ease-[cubic-bezier(0.23,1,0.32,1)] active:scale-[0.97] motion-reduce:transition-none motion-reduce:active:transform-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

type SiteHeaderProps = {
  projectName: string;
  items: NavigationItem[];
};

export function SiteHeader({ projectName, items }: SiteHeaderProps) {
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
    <header className="sticky top-0 z-40 border-b border-border bg-background pt-[env(safe-area-inset-top)]">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-2 px-4 sm:gap-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className={`${pressable} min-w-0 truncate rounded-md px-2 text-base font-semibold tracking-tight text-foreground`}
        >
          {projectName}
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
                    className={`${pressable} relative inline-flex h-11 items-center rounded-md px-3 text-sm font-medium ${
                      current
                        ? "text-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
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
          <button
            ref={menuButtonRef}
            type="button"
            className={`${pressable} inline-flex size-11 items-center justify-center rounded-md text-foreground hover:bg-muted md:hidden`}
            aria-expanded={open}
            aria-controls={menuId}
            aria-label={open ? "Menü schließen" : "Menü öffnen"}
            onClick={open ? closeMenu : openMenu}
          >
            {open ? <CloseIcon /> : <MenuIcon />}
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
            <p className="min-w-0 truncate font-semibold tracking-tight">{projectName}</p>
            <button
              type="button"
              className={`${pressable} inline-flex size-11 items-center justify-center rounded-md hover:bg-muted`}
              aria-label="Menü schließen"
              onClick={closeMenu}
            >
              <CloseIcon />
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
                      className={`${pressable} flex min-h-11 items-center rounded-md border-l-2 px-4 text-base font-medium ${
                        current
                          ? "border-foreground bg-muted text-foreground"
                          : "border-transparent text-muted-foreground hover:bg-muted hover:text-foreground"
                      }`}
                      onClick={closeMenu}
                    >
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
      </dialog>
    </header>
  );
}

function MenuIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="size-5 fill-none stroke-current stroke-[1.75]">
      <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="size-5 fill-none stroke-current stroke-[1.75]">
      <path d="M6 6l12 12M18 6 6 18" strokeLinecap="round" />
    </svg>
  );
}
