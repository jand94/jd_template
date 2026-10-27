import Link from "next/link";
import { ArrowRight, Cable, Layers, PanelsTopLeft, Tag } from "lucide-react";
import { Icon } from "@/components/ui/icon";
import { PageIntro } from "@/components/ui/page-intro";
import { buttonPrimary, buttonSecondary, panelClass } from "@/components/ui/styles";
import { brand } from "@/config/brand";

const cards = [
  {
    icon: PanelsTopLeft,
    label: "Oberfläche",
    title: "Navbar, Inhalt, Fußzeile",
    text: "Dieselbe Hülle gilt für jede Route, vom schmalen Bildschirm bis zum Desktop.",
  },
  {
    icon: Cable,
    label: "Schnittstelle",
    title: brand.apiTitle,
    text: "Titel und Beschreibung kommen aus der Umgebung.",
  },
  {
    icon: Tag,
    label: "Ausgabe",
    title: brand.apiVersion,
    text: "Version und Namen stehen auf der Systemseite.",
  },
] as const;

export default function Home() {
  return (
    <article className="flex flex-col gap-12">
      <div className="flex flex-col gap-8">
        <PageIntro
          icon={Layers}
          eyebrow="Vorlage"
          title={brand.projectName}
          description={brand.apiDescription}
        />
        <div className="flex flex-col gap-3 sm:flex-row">
          <Link href="/system" className={buttonPrimary}>
            System ansehen
            <Icon icon={ArrowRight} />
          </Link>
          <Link href="/anmelden" className={buttonSecondary}>
            Anmelden
          </Link>
        </div>
      </div>
      <section aria-labelledby="ueberblick-heading">
        <h2 id="ueberblick-heading" className="text-sm font-medium text-muted-foreground">
          Überblick
        </h2>
        <ul className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cards.map((card) => (
            <li key={card.label} className={panelClass}>
              <span className="inline-flex size-10 items-center justify-center rounded-lg bg-accent-soft text-accent">
                <Icon icon={card.icon} className="size-5" />
              </span>
              <h3 className="mt-4 text-sm text-muted-foreground">{card.label}</h3>
              <p className="mt-1 text-lg font-semibold tracking-tight break-words">{card.title}</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{card.text}</p>
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
