"use client";

import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { PageIntro } from "@/components/ui/page-intro";
import { panelClass } from "@/components/ui/styles";

type AuthPanelProps = {
  icon: LucideIcon;
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
};

export function AuthPanel({ icon, title, description, children, footer }: AuthPanelProps) {
  return (
    <article className="mx-auto w-full max-w-md">
      <div className={panelClass}>
        <PageIntro icon={icon} title={title} description={description} />
        <div className="mt-8">{children}</div>
        {footer ? <div className="mt-6 border-t border-border pt-5">{footer}</div> : null}
      </div>
    </article>
  );
}
