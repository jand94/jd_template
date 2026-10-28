import type { Metadata } from "next";
import { ProfileScreen } from "@/features/accounts";

export const metadata: Metadata = {
  title: "Profil",
};

export default function ProfilePage() {
  return <ProfileScreen />;
}
