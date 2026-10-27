import type { Metadata } from "next";
import { PasswordResetForm } from "@/features/accounts";

export const metadata: Metadata = {
  title: "Passwort vergessen",
};

export default function PasswordResetPage() {
  return <PasswordResetForm />;
}
