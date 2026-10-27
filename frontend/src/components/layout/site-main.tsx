import type { ReactNode } from "react";

type SiteMainProps = {
  children: ReactNode;
};

export function SiteMain({ children }: SiteMainProps) {
  return (
    <main
      id="main"
      tabIndex={-1}
      className="flex-1 scroll-mt-16 outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-ring"
    >
      <div className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
        {children}
      </div>
    </main>
  );
}
