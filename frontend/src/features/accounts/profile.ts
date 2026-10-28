import type { Account } from "@/features/accounts/api/session";

export function mediaUrl(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }
  if (value.startsWith("blob:") || value.startsWith("data:")) {
    return value;
  }
  if (value.startsWith("http://") || value.startsWith("https://")) {
    try {
      return new URL(value).pathname;
    } catch {
      return null;
    }
  }
  return value.startsWith("/") ? value : `/${value}`;
}

export function accountDisplayName(user: Pick<Account, "preferred_name" | "title" | "first_name" | "middle_name" | "last_name" | "username">): string {
  if (user.preferred_name && user.last_name) {
    return `${user.preferred_name} ${user.last_name}`;
  }
  if (user.preferred_name) {
    return user.preferred_name;
  }
  const full = [user.title, user.first_name, user.middle_name, user.last_name].filter(Boolean).join(" ");
  return full || user.username;
}

export function accountInitials(user: Pick<Account, "preferred_name" | "first_name" | "last_name" | "username">): string {
  const first = (user.preferred_name || user.first_name).trim().charAt(0);
  const last = user.last_name.trim().charAt(0);
  const letters = `${first}${last}`.toUpperCase();
  return letters || user.username.slice(0, 2).toUpperCase();
}
