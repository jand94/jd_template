import type { ReactNode } from "react";
import { AuthShell } from "@/components/layout/auth-shell";
import { RedirectIfAuthenticated } from "@/features/accounts";

export const instant = false;

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <AuthShell>
      <RedirectIfAuthenticated>{children}</RedirectIfAuthenticated>
    </AuthShell>
  );
}
