import type { Metadata } from "next";
import { FileText, Hash, Layers, Server } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Icon } from "@/components/ui/icon";
import { PageIntro } from "@/components/ui/page-intro";
import { panelClass } from "@/components/ui/styles";
import { brand } from "@/config/brand";

export const metadata: Metadata = {
  title: "System",
  description: brand.apiDescription,
};

const rows: { term: string; value: string; icon: LucideIcon }[] = [
  { term: "Projekt", value: brand.projectName, icon: Layers },
  { term: "Schnittstelle", value: brand.apiTitle, icon: Server },
  { term: "Beschreibung", value: brand.apiDescription, icon: FileText },
  { term: "Version", value: brand.apiVersion, icon: Hash },
];

export default function SystemPage() {
  return (
    <article>
      <PageIntro
        icon={Server}
        eyebrow="Umgebung"
        title="System"
        description="Sichtbare Namen dieser Ausgabe, gelesen aus der Umgebung."
      />
      <dl className="mt-10 grid gap-4 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.term} className={panelClass}>
            <dt className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="inline-flex size-8 items-center justify-center rounded-lg bg-accent-soft text-accent">
                <Icon icon={row.icon} />
              </span>
              {row.term}
            </dt>
            <dd className="mt-4 text-lg font-medium tracking-tight break-words">{row.value}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
