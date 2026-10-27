import type { LucideIcon } from "lucide-react";

type IconProps = {
  icon: LucideIcon;
  className?: string;
};

export function Icon({ icon: Glyph, className = "size-4" }: IconProps) {
  return <Glyph aria-hidden="true" strokeWidth={1.75} className={className} />;
}
