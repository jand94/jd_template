"use client";

import { useSearchParams } from "next/navigation";
import { EmailConfirmForm } from "@/features/accounts/components/email-confirm-form";

export function EmailConfirmScreen() {
  const params = useSearchParams();
  return <EmailConfirmForm uid={params.get("uid") ?? ""} token={params.get("token") ?? ""} />;
}
