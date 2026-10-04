import { afterEach, describe, expect, it, vi } from "vitest";

import { focusMap } from "./focusMap.ts";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("focusMap", () => {
  it("moves the focus to the canvas of the map", () => {
    const focus = vi.fn();
    const querySelector = vi.fn(() => ({ focus }));
    vi.stubGlobal("document", { querySelector });

    focusMap();

    expect(querySelector).toHaveBeenCalledWith(".maplibregl-canvas");
    expect(focus).toHaveBeenCalledTimes(1);
  });

  it("does nothing where no map is drawn", () => {
    vi.stubGlobal("document", { querySelector: () => null });

    expect(() => focusMap()).not.toThrow();
  });
});
