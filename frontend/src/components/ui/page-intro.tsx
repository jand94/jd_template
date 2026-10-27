import type { LucideIcon } from "lucide-react";
import { Icon } from "@/components/ui/icon";

type PageIntroProps = {
  title: string;
  description?: string;
  eyebrow?: string;
  icon?: LucideIcon;
};

export function PageIntro({ title, description, eyebrow, icon }: PageIntroProps) {
  return (
    <header className="flex max-w-2xl flex-col gap-4">
      {icon ? (
        <span className="inline-flex size-11 items-center justify-center rounded-xl bg-accent-soft text-accent">
          <Icon icon={icon} className="size-5" />
        </span>
      ) : null}
      <div>
        {eyebrow ? <p className="text-sm font-medium text-accent">{eyebrow}</p> : null}
        <h1 className="text-3xl font-semibold tracking-tight text-balance sm:text-4xl">{title}</h1>
        {description ? (
          <p className="mt-3 text-base leading-7 text-pretty break-words text-muted-foreground">
            {description}
          </p>
        ) : null}
      </div>
    </header>
  );
}
