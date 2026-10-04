import { Outlet } from "react-router";

import { ReportDraftProvider } from "../../state/reportDraft.tsx";

/**
 * The frame of the flow that reports a barrier, an amenity or an area. It keeps the draft of the report for its steps,
 * so the draft lives as long as the flow is open and is gone when a person leaves it.
 */
export function ReportFlow() {
  return (
    <ReportDraftProvider>
      <Outlet />
    </ReportDraftProvider>
  );
}
