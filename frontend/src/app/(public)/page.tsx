import Link from "next/link";
import { brand } from "@/config/brand";

export default function Home() {
  return (
    <article className="flex flex-col gap-12">
      <header className="max-w-2xl">
        <h1 className="text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
          {brand.projectName}
        </h1>
        <p className="mt-4 text-lg leading-8 text-pretty break-words text-muted-foreground">
          {brand.apiDescription}
        </p>
      </header>
      <section aria-labelledby="ueberblick-heading">
        <h2 id="ueberblick-heading" className="text-sm font-semibold">
          Überblick
        </h2>
        <ul className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <li className="rounded-lg border border-border p-5">
            <h3 className="text-sm text-muted-foreground">Oberfläche</h3>
            <p className="mt-2 text-lg font-semibold tracking-tight">
              Navbar, Inhalt, Fußzeile
            </p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Dieselbe Hülle gilt für jede Route, vom schmalen Bildschirm bis zum Desktop.
            </p>
          </li>
          <li className="rounded-lg border border-border p-5">
            <h3 className="text-sm text-muted-foreground">Schnittstelle</h3>
            <p className="mt-2 text-lg font-semibold tracking-tight break-words">
              {brand.apiTitle}
            </p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Titel und Beschreibung kommen aus der Umgebung.
            </p>
          </li>
          <li className="rounded-lg border border-border p-5">
            <h3 className="text-sm text-muted-foreground">Ausgabe</h3>
            <p className="mt-2 text-lg font-semibold tracking-tight">{brand.apiVersion}</p>
            <p className="mt-3">
              <Link
                href="/system"
                className="inline-flex min-h-11 items-center text-sm font-medium text-foreground underline decoration-border underline-offset-4 cursor-pointer hover:decoration-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                System ansehen
              </Link>
            </p>
          </li>
        </ul>
      </section>
    </article>
  );
}
