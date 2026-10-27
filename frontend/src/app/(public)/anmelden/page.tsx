import type { Metadata } from "next";
import { LoginForm } from "@/features/accounts";

export const metadata: Metadata = {
  title: "Anmelden",
};

export default function LoginPage() {
  return <LoginForm />;
}
