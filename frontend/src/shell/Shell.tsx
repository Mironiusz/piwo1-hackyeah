import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, Outlet, useLocation } from "react-router";

import { Button } from "../parts/Button.tsx";
import { Note } from "../parts/Note.tsx";
import { rememberLastMapPath } from "../state/lastMapPath.ts";
import { useNeeds } from "../state/needs.tsx";
import { useSession } from "../state/session.tsx";
import { BottomBar } from "./BottomBar.tsx";
import { ErrorBoundary } from "./ErrorBoundary.tsx";
import { Header } from "./Header.tsx";
import { Menu } from "./Menu.tsx";

const NEEDS_PATH = "/needs";
const MAP_PATH_PATTERN = /^\/($|fact\/|route($|\/))/;

/**
 * Tells which entry of the bottom bar a path belongs to.
 */
function findCurrentTab(path: string): "map" | "report" | "needs" | "other" {
  if (MAP_PATH_PATTERN.test(path)) {
    return "map";
  }
  if (path === "/report" || path.startsWith("/report/")) {
    return "report";
  }
  return path === NEEDS_PATH ? "needs" : "other";
}

/**
 * The frame of every view: the header with the menu, the view, and the bottom bar.
 * On the first opening on a device it shows the needs before anything else, and counts the opening as done once a person leaves them.
 * When the address changes it moves the focus to the heading of the view when the heading takes focus, and to the view otherwise,
 * closes the menu, remembers the map mode a person left,
 * and tells once that a session ended.
 */
export function Shell() {
  const { t } = useTranslation();
  const location = useLocation();
  const { needs, markSeen } = useNeeds();
  const { hasEnded, dismissEnded } = useSession();
  const [menuPath, setMenuPath] = useState<string | null>(null);
  const [mapPath, setMapPath] = useState("/");
  const [wasOnNeeds, setWasOnNeeds] = useState(false);
  const main = useRef<HTMLElement | null>(null);
  const isFirstRender = useRef(true);
  const path = location.pathname;
  const current = findCurrentTab(path);
  const isMenuOpen = menuPath === path;

  if (current === "map" && mapPath !== path) {
    setMapPath(path);
  }
  if (path === NEEDS_PATH && !wasOnNeeds) {
    setWasOnNeeds(true);
  }

  useEffect(() => {
    if (findCurrentTab(path) === "map") {
      rememberLastMapPath(path);
    }
    if (wasOnNeeds && path !== NEEDS_PATH) {
      markSeen();
    }
  }, [path, wasOnNeeds, markSeen]);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const heading = main.current?.querySelector<HTMLElement>('h1[tabindex="-1"]');
    (heading ?? main.current)?.focus({ preventScroll: true });
    main.current?.scrollTo({ top: 0 });
  }, [path]);

  useEffect(() => {
    if (!isMenuOpen) {
      return undefined;
    }
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMenuPath(null);
        document.getElementById("menu-button")?.focus();
      }
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [isMenuOpen]);

  if (!needs.isSeen && !wasOnNeeds && path !== NEEDS_PATH) {
    return <Navigate to={NEEDS_PATH} replace />;
  }

  return (
    <div className="app-frame mx-auto flex w-full max-w-[520px] flex-col bg-bg shadow-[0_0_24px_rgba(17,20,24,0.12)]">
      <Header isMenuOpen={isMenuOpen} onToggleMenu={() => setMenuPath(isMenuOpen ? null : path)} showsLanguage={!needs.isSeen} />
      <div className="relative flex min-h-0 flex-1 flex-col">
        {isMenuOpen ? <Menu onClose={() => setMenuPath(null)} /> : null}
        <main ref={main} tabIndex={-1} className="flex min-h-0 flex-1 flex-col overflow-x-hidden overflow-y-auto outline-none">
          {hasEnded ? (
            <div className="flex-none bg-surface px-4 pt-3">
              <Note kind="strong" announce="alert">
                <p>{t("account.session_expired")}</p>
                <div className="mt-2 flex gap-2.5">
                  <Button isSmall look="primary" to="/account">
                    {t("account.log_in")}
                  </Button>
                  <Button isSmall onClick={dismissEnded}>
                    {t("action.close")}
                  </Button>
                </div>
              </Note>
            </div>
          ) : null}
          <ErrorBoundary resetKey={path}>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <BottomBar current={current} mapPath={mapPath} />
    </div>
  );
}
