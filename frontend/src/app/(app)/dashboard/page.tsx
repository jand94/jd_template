import type { Metadata } from "next";
import { DashboardScreen } from "@/features/accounts";

export const metadata: Metadata = {
  title: "Dashboard",
};

export default function DashboardPage() {
  return <DashboardScreen />;
}
