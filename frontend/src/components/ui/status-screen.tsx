import type { ReactNode } from "react";

type StatusScreenProps = {
  code: string;
  title: string;
  description: string;
  action?: ReactNode;
};

export function StatusScreen({ code, title, description, action }: StatusScreenProps) {
  return (
    <main
      id="main"
      tabIndex={-1}
      className="mx-auto flex w-full max-w-6xl flex-1 flex-col justify-center px-4 py-16 outline-none sm:px-6 lg:px-8"
    >
      <p className="text-sm font-medium text-accent">{code}</p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight text-balance">{title}</h1>
      <p className="mt-3 max-w-xl text-base leading-7 text-pretty text-muted-foreground">
        {description}
      </p>
      {action ? <div className="mt-8">{action}</div> : null}
    </main>
  );
}
