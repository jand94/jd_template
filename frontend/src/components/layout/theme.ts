export const THEME_STORAGE_KEY = "theme";

export type ThemeMode = "light" | "dark" | "system";

export function isThemeMode(value: string | null): value is ThemeMode {
  return value === "light" || value === "dark" || value === "system";
}

const themeListeners = new Set<() => void>();

export function subscribeTheme(listener: () => void) {
  themeListeners.add(listener);
  return () => themeListeners.delete(listener);
}

export function readTheme(): ThemeMode {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  return isThemeMode(stored) ? stored : "system";
}

export function applyTheme(mode: ThemeMode) {
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const dark = mode === "dark" || (mode === "system" && prefersDark);
  const root = document.documentElement;
  root.classList.toggle("dark", dark);
  root.classList.toggle("light", mode === "light");
}

export function writeTheme(mode: ThemeMode) {
  localStorage.setItem(THEME_STORAGE_KEY, mode);
  applyTheme(mode);
  for (const listener of themeListeners) {
    listener();
  }
}

export const themeBootScript = `(function(){try{var stored=localStorage.getItem(${JSON.stringify(THEME_STORAGE_KEY)});var mode=stored==="light"||stored==="dark"?stored:"system";var prefersDark=window.matchMedia("(prefers-color-scheme: dark)").matches;var dark=mode==="dark"||(mode==="system"&&prefersDark);var root=document.documentElement;root.classList.toggle("dark",dark);root.classList.toggle("light",mode==="light");}catch(e){}})();`;
