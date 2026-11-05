import type { Metadata } from "next";
import { Suspense } from "react";
import { PasswordSetScreen } from "@/features/accounts";

export const metadata: Metadata = {
  title: "Neues Passwort",
};

export default function PasswordSetPage() {
  return (
    <Suspense fallback={null}>
      <PasswordSetScreen />
    </Suspense>
  );
}
