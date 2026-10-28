"use client";

import Image from "next/image";
import { useState } from "react";
import type { Account } from "@/features/accounts/api/session";
import { accountInitials, mediaUrl } from "@/features/accounts/profile";

type AccountAvatarProps = {
  user: Pick<Account, "avatar" | "preferred_name" | "first_name" | "last_name" | "username">;
  className?: string;
  alt?: string;
};

export function AccountAvatar({ user, className = "size-10", alt = "" }: AccountAvatarProps) {
  const src = mediaUrl(user.avatar);
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  const failed = src !== null && failedSrc === src;

  if (!src || failed) {
    return (
      <span
        aria-hidden={alt ? undefined : true}
        className={`inline-flex items-center justify-center rounded-full bg-accent-soft text-sm font-semibold text-accent ${className}`}
      >
        {accountInitials(user)}
      </span>
    );
  }

  if (src.startsWith("blob:") || src.startsWith("data:")) {
    return (
      // Die lokale Vorschau ist eine Blob-Adresse. next/image lädt die nicht.
      // eslint-disable-next-line @next/next/no-img-element
      <img src={src} alt={alt} className={`rounded-full object-cover ${className}`} />
    );
  }

  return (
    <span className={`relative inline-flex overflow-hidden rounded-full ${className}`}>
      <Image
        src={src}
        alt={alt}
        fill
        unoptimized
        sizes="96px"
        className="object-cover"
        onError={() => setFailedSrc(src)}
      />
    </span>
  );
}
