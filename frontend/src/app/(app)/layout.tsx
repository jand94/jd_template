import type { ReactNode } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { AccountLinks, AccountMenu, RequireAccount } from "@/features/accounts";

export const instant = false;

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <AppShell accountMenu={<AccountMenu />} mobileAccount={<AccountLinks />}>
      <RequireAccount>{children}</RequireAccount>
    </AppShell>
  );
}
