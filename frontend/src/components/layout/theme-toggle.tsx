"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useEffect, useSyncExternalStore } from "react";
import { Icon } from "@/components/ui/icon";
import { focusRing, pressable } from "@/components/ui/styles";
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

const icons = {
  system: Monitor,
  light: Sun,
  dark: Moon,
} as const;

export function ThemeToggle() {
  const mode = useSyncExternalStore<ThemeMode>(subscribeTheme, readTheme, () => "system");

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
      className={`${pressable} ${focusRing} inline-flex h-11 items-center gap-2 rounded-lg px-3 text-foreground hover:bg-muted`}
      aria-label={`Darstellung wechseln, aktuell ${labels[mode]}`}
      onClick={cycle}
    >
      <Icon icon={icons[mode]} className="size-5" />
      <span className="hidden min-w-14 text-left text-sm font-medium sm:inline">
        {labels[mode]}
      </span>
    </button>
  );
}
