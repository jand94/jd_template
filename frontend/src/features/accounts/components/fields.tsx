"use client";

import { CircleAlert, LoaderCircle, type LucideIcon } from "lucide-react";
import { useId, type InputHTMLAttributes, type ReactNode } from "react";
import { Icon } from "@/components/ui/icon";
import { buttonPrimary, focusRing } from "@/components/ui/styles";

const control = `h-11 w-full rounded-lg border border-border bg-background text-base text-foreground outline-none ${focusRing}`;

type TextFieldProps = {
  label: string;
  name: string;
  type?: string;
  autoComplete?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  icon?: LucideIcon;
} & Pick<InputHTMLAttributes<HTMLInputElement>, "value" | "onChange">;

export function TextField({
  label,
  name,
  type = "text",
  autoComplete,
  error,
  hint,
  required,
  icon,
  value,
  onChange,
}: TextFieldProps) {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      <div className="relative">
        {icon ? (
          <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-muted-foreground">
            <Icon icon={icon} />
          </span>
        ) : null}
        <input
          id={id}
          name={name}
          type={type}
          autoComplete={autoComplete}
          required={required}
          value={value}
          onChange={onChange}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(error ? errorId : undefined, hint ? hintId : undefined)}
        className={`${control} ${icon ? "pr-3 pl-10" : "px-3"}`}
      />
      </div>
      {hint ? (
        <p id={hintId} className="text-sm text-muted-foreground">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

type Choice = { value: string; label: string };

export function SelectField({
  label,
  name,
  value,
  onChange,
  options,
  error,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  options: Choice[];
  error?: string;
}) {
  const id = useId();
  const errorId = `${id}-error`;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      <select
        id={id}
        name={name}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        className={`${control} px-3`}
      >
        {options.map((option) => (
          <option key={option.value || "empty"} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error ? (
        <p id={errorId} className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function TextArea({
  label,
  name,
  value,
  onChange,
  error,
  hint,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  hint?: string;
}) {
  const id = useId();
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      <textarea
        id={id}
        name={name}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={4}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(error ? errorId : undefined, hint ? hintId : undefined)}
        className={`${control} h-auto min-h-28 px-3 py-2`}
      />
      {hint ? (
        <p id={hintId} className="text-sm text-muted-foreground">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

function describedBy(...ids: Array<string | undefined>): string | undefined {
  const value = ids.filter(Boolean).join(" ");
  return value || undefined;
}

export function FormError({ children }: { children: ReactNode }) {
  if (!children) {
    return null;
  }

  return (
    <p role="alert" className="flex items-start gap-2 rounded-lg bg-danger-soft px-3 py-2.5 text-sm text-danger">
      <Icon icon={CircleAlert} className="mt-0.5 size-4 shrink-0" />
      <span>{children}</span>
    </p>
  );
}

export function FormStatus({ children }: { children: ReactNode }) {
  return (
    <p role="status" className="flex items-start gap-2 rounded-lg bg-success-soft px-3 py-2.5 text-sm text-success">
      {children}
    </p>
  );
}

export function SubmitButton({ pending, children }: { pending: boolean; children: string }) {
  return (
    <button type="submit" disabled={pending} className={`${buttonPrimary} w-full`}>
      {pending ? <Icon icon={LoaderCircle} className="size-4 animate-spin motion-reduce:animate-none" /> : null}
      {pending ? "Wird gesendet" : children}
    </button>
  );
}
