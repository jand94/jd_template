import type { ReactNode } from "react";
import { brand } from "@/config/brand";
import { primaryNavigation } from "@/config/navigation";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteMain } from "@/components/layout/site-main";

const pressable =
  "cursor-pointer touch-manipulation rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background transition-transform duration-150 ease-[cubic-bezier(0.23,1,0.32,1)] active:scale-[0.97] motion-reduce:transition-none motion-reduce:active:transform-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <>
      <a
        href="#main"
        className={`fixed top-4 left-4 z-50 -translate-y-24 ${pressable} focus:translate-y-0`}
      >
        Zum Inhalt springen
      </a>
      <SiteHeader projectName={brand.projectName} items={primaryNavigation} />
      <SiteMain>{children}</SiteMain>
      <SiteFooter
        projectName={brand.projectName}
        description={brand.apiDescription}
        apiTitle={brand.apiTitle}
        version={brand.apiVersion}
        items={primaryNavigation}
      />
    </>
  );
}
