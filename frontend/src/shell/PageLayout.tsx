import { Outlet } from "react-router";

/**
 * The layout of the views that are pages without the map: the needs, the account, the privacy information,
 * the page about the data and moderation.
 */
export function PageLayout() {
  return (
    <div className="flex-1 bg-surface px-4 pt-[18px] pb-[22px]">
      <Outlet />
    </div>
  );
}
