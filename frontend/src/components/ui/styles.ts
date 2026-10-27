export const focusRing =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

export const pressable =
  "cursor-pointer touch-manipulation transition-[color,background-color,border-color,transform] duration-150 ease-[cubic-bezier(0.23,1,0.32,1)] active:scale-[0.97] motion-reduce:transition-none motion-reduce:active:transform-none";

export const buttonPrimary = `inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-foreground px-4 text-sm font-medium text-background ${pressable} ${focusRing} disabled:cursor-wait disabled:opacity-60`;

export const buttonSecondary = `inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 text-sm font-medium text-foreground hover:bg-muted ${pressable} ${focusRing}`;

export const panelClass = "rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow)] sm:p-8";
