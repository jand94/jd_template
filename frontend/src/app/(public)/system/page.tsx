import type { Metadata } from "next";
import { brand } from "@/config/brand";

export const metadata: Metadata = {
  title: "System",
  description: brand.apiDescription,
};

export default function SystemPage() {
  return (
    <article className="max-w-2xl">
      <header>
        <h1 className="text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
          System
        </h1>
        <p className="mt-4 text-lg leading-8 text-pretty text-muted-foreground">
          Sichtbare Namen dieser Ausgabe, gelesen aus der Umgebung.
        </p>
      </header>
      <dl className="mt-10 divide-y divide-border border-y border-border">
        <SystemRow term="Projekt" value={brand.projectName} />
        <SystemRow term="Schnittstelle" value={brand.apiTitle} />
        <SystemRow term="Beschreibung" value={brand.apiDescription} />
        <SystemRow term="Version" value={brand.apiVersion} />
      </dl>
    </article>
  );
}

function SystemRow({ term, value }: { term: string; value: string }) {
  return (
    <div className="grid gap-1 py-4 sm:grid-cols-[10rem_1fr] sm:gap-6">
      <dt className="text-sm text-muted-foreground">{term}</dt>
      <dd className="text-base font-medium break-words">{value}</dd>
    </div>
  );
}
