import type { ButtonHTMLAttributes, ReactNode } from "react";

export function DovetMark({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path fill="currentColor" d="M2 5h9l3 3-3 3H2V5Zm20 14h-9l-3-3 3-3h9v6Z" />
    </svg>
  );
}

export function Status({ tone, children }: { tone: "ready" | "warning" | "danger"; children: ReactNode }) {
  return <span className={`status status--${tone}`}><span aria-hidden="true">●</span>{children}</span>;
}

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={["button", props.className].filter(Boolean).join(" ")} />;
}

