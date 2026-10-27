import type { ReactNode } from "react";
import { buttonPrimary } from "@/components/ui/styles";
import { brand } from "@/config/brand";
import { primaryNavigation } from "@/config/navigation";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteMain } from "@/components/layout/site-main";

type AppShellProps = {
  children: ReactNode;
  accountMenu: ReactNode;
  mobileAccount: ReactNode;
};

export function AppShell({ children, accountMenu, mobileAccount }: AppShellProps) {
  return (
    <>
      <a
        href="#main"
        className={`fixed top-4 left-4 z-50 -translate-y-24 ${buttonPrimary} focus:translate-y-0`}
      >
        Zum Inhalt springen
      </a>
      <SiteHeader
        projectName={brand.projectName}
        items={primaryNavigation}
        accountMenu={accountMenu}
        mobileAccount={mobileAccount}
      />
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
