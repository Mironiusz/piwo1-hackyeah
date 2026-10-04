import type { ReactNode } from "react";

interface NoteProps {
  kind?: "plain" | "dash" | "strong";
  title?: string;
  announce?: "status" | "alert";
  className?: string;
  children: ReactNode;
}

const KINDS: Record<NonNullable<NoteProps["kind"]>, string> = {
  plain: "border border-line",
  dash: "border-[1.5px] border-dashed border-nodata",
  strong: "border-[1.5px] border-ink",
};

/**
 * A message of a view. The plain kind tells what happened, the dashed kind marks missing data,
 * and the strong kind marks that something could not be done. With announce set, a screen reader reads it out when it appears:
 * status waits for a pause, and alert interrupts.
 */
export function Note({ kind = "plain", title, announce, className = "", children }: NoteProps) {
  return (
    <div role={announce} className={`rounded-panel bg-surface px-3 py-2.5 text-[13.5px] ${KINDS[kind]} ${className}`}>
      {title !== undefined ? <p className="font-bold">{title}</p> : null}
      {children}
    </div>
  );
}
