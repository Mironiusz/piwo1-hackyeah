import { BrowserRouter, Route, Routes } from "react-router";

import { MapLayout } from "./shell/MapLayout.tsx";
import { NotFound } from "./shell/NotFound.tsx";
import { PageLayout } from "./shell/PageLayout.tsx";
import { Shell } from "./shell/Shell.tsx";
import { NeedsProvider } from "./state/needs.tsx";
import { PlannedRouteProvider } from "./state/plannedRoute.tsx";
import { SessionProvider } from "./state/session.tsx";
import { AboutDataView } from "./views/AboutDataView.tsx";
import { AccountView } from "./views/AccountView.tsx";
import { AddressSearchView } from "./views/AddressSearchView.tsx";
import { FactDetailPanel } from "./views/FactDetailPanel.tsx";
import { FactsMapView } from "./views/FactsMapView.tsx";
import { ModerationView } from "./views/ModerationView.tsx";
import { NeedsView } from "./views/NeedsView.tsx";
import { PointPickView } from "./views/PointPickView.tsx";
import { PrivacyView } from "./views/PrivacyView.tsx";
import { ReportDetailsStep } from "./views/report/ReportDetailsStep.tsx";
import { ReportExistingStep } from "./views/report/ReportExistingStep.tsx";
import { ReportFlow } from "./views/report/ReportFlow.tsx";
import { ReportKindStep } from "./views/report/ReportKindStep.tsx";
import { ReportPlaceStep } from "./views/report/ReportPlaceStep.tsx";
import { ReportSavedStep } from "./views/report/ReportSavedStep.tsx";
import { ReportSummaryStep } from "./views/report/ReportSummaryStep.tsx";
import { RoutePlanningView } from "./views/RoutePlanningView.tsx";
import { RouteResultView } from "./views/RouteResultView.tsx";

/**
 * The application: the state kept for every view, and the addresses of the views.
 * The views with the map share one layout, so the map stays while its panel changes; the pages share the other.
 * The menu is a layer of the shell and has no address.
 */
export function App() {
  return (
    <SessionProvider>
      <NeedsProvider>
        <PlannedRouteProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Shell />}>
                <Route element={<MapLayout />}>
                  <Route path="/" element={<FactsMapView />}>
                    <Route path="fact/:factId" element={<FactDetailPanel />} />
                  </Route>
                  <Route path="route" element={<RoutePlanningView />} />
                  <Route path="route/search/:end" element={<AddressSearchView />} />
                  <Route path="route/pick/:end" element={<PointPickView />} />
                  <Route path="route/result" element={<RouteResultView />}>
                    <Route path="fact/:factId" element={<FactDetailPanel />} />
                  </Route>
                  <Route path="report" element={<ReportFlow />}>
                    <Route index element={<ReportKindStep />} />
                    <Route path="place" element={<ReportPlaceStep />} />
                    <Route path="details" element={<ReportDetailsStep />} />
                    <Route path="existing" element={<ReportExistingStep />} />
                    <Route path="summary" element={<ReportSummaryStep />} />
                    <Route path="saved" element={<ReportSavedStep />} />
                  </Route>
                </Route>
                <Route element={<PageLayout />}>
                  <Route path="needs" element={<NeedsView />} />
                  <Route path="account" element={<AccountView />} />
                  <Route path="privacy" element={<PrivacyView />} />
                  <Route path="about-data" element={<AboutDataView />} />
                  <Route path="moderation" element={<ModerationView />} />
                  <Route path="*" element={<NotFound />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
        </PlannedRouteProvider>
      </NeedsProvider>
    </SessionProvider>
  );
}
