import type { ReactNode } from "react";

import { MapResizeHandle } from "./MapResizeHandle.tsx";

interface PanelProps {
  label?: string;
  labelledBy?: string;
  isPadded?: boolean;
  children: ReactNode;
}

/**
 * The panel that lies over the lower part of the map and carries the content of a map view.
 * It fills the screen below the map and is a named region, so a screen reader can jump to it past the map.
 * The bar at its top changes the height of the map.
 */
export function Panel({ label, labelledBy, isPadded = true, children }: PanelProps) {
  return (
    <section aria-label={label} aria-labelledby={labelledBy} className="relative z-[3] -mt-3.5 flex-1 rounded-t-sheet bg-surface pt-[18px] shadow-sheet">
      <MapResizeHandle />
      {isPadded ? <div className="px-4 pt-1 pb-[18px]">{children}</div> : children}
    </section>
  );
}
