"use client";

import { useEffect, useSyncExternalStore } from "react";
import {
  applyTheme,
  readTheme,
  subscribeTheme,
  writeTheme,
  type ThemeMode,
} from "@/components/layout/theme";

const labels: Record<ThemeMode, string> = {
  system: "System",
  light: "Hell",
  dark: "Dunkel",
};

const nextMode: Record<ThemeMode, ThemeMode> = {
  system: "light",
  light: "dark",
  dark: "system",
};

const pressable =
  "cursor-pointer touch-manipulation rounded-md transition-[color,background-color,transform] duration-150 ease-[cubic-bezier(0.23,1,0.32,1)] active:scale-[0.97] motion-reduce:transition-none motion-reduce:active:transform-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

export function ThemeToggle() {
  const mode = useSyncExternalStore(subscribeTheme, readTheme, () => "system");

  useEffect(() => {
    if (mode !== "system") {
      return;
    }

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => applyTheme("system");
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, [mode]);

  function cycle() {
    writeTheme(nextMode[mode]);
  }

  return (
    <button
      type="button"
      className={`${pressable} inline-flex h-11 items-center gap-2 px-3 text-foreground hover:bg-muted`}
      aria-label={`Darstellung wechseln, aktuell ${labels[mode]}`}
      onClick={cycle}
    >
      <ThemeIcon mode={mode} />
      <span className="hidden min-w-14 text-left text-sm font-medium sm:inline">
        {labels[mode]}
      </span>
    </button>
  );
}

function ThemeIcon({ mode }: { mode: ThemeMode }) {
  if (mode === "light") {
    return (
      <svg aria-hidden="true" viewBox="0 0 24 24" className="size-5 fill-none stroke-current stroke-[1.75]">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4" strokeLinecap="round" />
      </svg>
    );
  }

  if (mode === "dark") {
    return (
      <svg aria-hidden="true" viewBox="0 0 24 24" className="size-5 fill-none stroke-current stroke-[1.75]">
        <path d="M20 14.5A7.5 7.5 0 0 1 9.5 4 7 7 0 1 0 20 14.5Z" strokeLinejoin="round" />
      </svg>
    );
  }

  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="size-5 fill-none stroke-current stroke-[1.75]">
      <rect x="3" y="4" width="18" height="13" rx="2" />
      <path d="M8 21h8M12 17v4" strokeLinecap="round" />
    </svg>
  );
}
