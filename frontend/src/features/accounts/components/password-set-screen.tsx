"use client";

import { useSearchParams } from "next/navigation";
import { PasswordSetForm } from "@/features/accounts/components/password-set-form";

export function PasswordSetScreen() {
  const params = useSearchParams();
  return <PasswordSetForm uid={params.get("uid") ?? ""} token={params.get("token") ?? ""} />;
}
