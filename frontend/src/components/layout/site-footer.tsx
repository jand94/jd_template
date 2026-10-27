import Link from "next/link";
import type { NavigationItem } from "@/config/navigation";

type SiteFooterProps = {
  projectName: string;
  description: string;
  apiTitle: string;
  version: string;
  items: NavigationItem[];
};

export function SiteFooter({
  projectName,
  description,
  apiTitle,
  version,
  items,
}: SiteFooterProps) {
  return (
    <footer className="mt-auto border-t border-border pb-[env(safe-area-inset-bottom)]">
      <div className="mx-auto grid w-full max-w-6xl gap-10 px-4 py-12 sm:px-6 md:grid-cols-2 lg:grid-cols-4 lg:px-8">
        <div className="md:col-span-2">
          <p className="text-base font-semibold tracking-tight">{projectName}</p>
          <p className="mt-3 max-w-md text-sm leading-6 text-pretty break-words text-muted-foreground">
            {description}
          </p>
        </div>
        <nav aria-label="Fußzeile">
          <h2 className="text-sm font-semibold">Projekt</h2>
          <ul className="mt-3 flex flex-col gap-1">
            {items.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="inline-flex min-h-11 items-center rounded-md text-sm text-muted-foreground cursor-pointer touch-manipulation hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div>
          <h2 className="text-sm font-semibold">Ausgabe</h2>
          <dl className="mt-3 flex flex-col gap-3 text-sm">
            <div>
              <dt className="text-muted-foreground">Schnittstelle</dt>
              <dd className="mt-1 font-medium break-words">{apiTitle}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Version</dt>
              <dd className="mt-1 font-medium">{version}</dd>
            </div>
          </dl>
        </div>
      </div>
      <div className="border-t border-border">
        <p className="mx-auto max-w-6xl px-4 py-4 text-sm text-muted-foreground sm:px-6 lg:px-8">
          © {projectName}
        </p>
      </div>
    </footer>
  );
}
