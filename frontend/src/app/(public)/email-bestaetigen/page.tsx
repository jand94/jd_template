import type { Metadata } from "next";
import { Suspense } from "react";
import { EmailConfirmScreen } from "@/features/accounts";

export const metadata: Metadata = {
  title: "E-Mail bestätigen",
};

export default function EmailConfirmPage() {
  return (
    <Suspense fallback={null}>
      <EmailConfirmScreen />
    </Suspense>
  );
}
