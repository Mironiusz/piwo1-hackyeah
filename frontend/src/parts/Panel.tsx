import type { ReactNode } from "react";

interface PanelProps {
  label?: string;
  labelledBy?: string;
  isPadded?: boolean;
  children: ReactNode;
}

/**
 * The panel that lies over the lower part of the map and carries the content of a map view.
 * It fills the screen below the map and is a named region, so a screen reader can jump to it past the map.
 */
export function Panel({ label, labelledBy, isPadded = true, children }: PanelProps) {
  return (
    <section
      aria-label={label}
      aria-labelledby={labelledBy}
      className="relative z-[3] -mt-3.5 flex-1 rounded-t-sheet bg-surface pt-[18px] shadow-sheet before:absolute before:top-[7px] before:left-1/2 before:-ml-[18px] before:h-1 before:w-9 before:rounded-[2px] before:bg-line"
    >
      {isPadded ? <div className="px-4 pt-1 pb-[18px]">{children}</div> : children}
    </section>
  );
}
