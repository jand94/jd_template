import Link from "next/link";
import { StatusScreen } from "@/components/ui/status-screen";
import { buttonPrimary } from "@/components/ui/styles";

export default function NotFound() {
  return (
    <StatusScreen
      code="404"
      title="Diese Seite gibt es nicht"
      description="Die Adresse ist unbekannt oder der Eintrag wurde verschoben."
      action={
        <Link href="/" className={buttonPrimary}>
          Zur Startseite
        </Link>
      }
    />
  );
}
