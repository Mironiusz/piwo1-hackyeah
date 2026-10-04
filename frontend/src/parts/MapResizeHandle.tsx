import { useEffect, useRef, useState, type ChangeEvent, type KeyboardEvent, type PointerEvent } from "react";
import { useTranslation } from "react-i18next";

import { useMap, type MapSpan } from "../map/mapScene.ts";

const KEY_STEP_PX = 40;

/**
 * The bar at the top of the panel that changes the height of the map above it.
 * A person drags the bar with a finger or a mouse. Inside it lies a native range input in pixels,
 * which takes the focus and tells a screen reader the height of the map. An arrow key moves the map by 40 pixels
 * and Home and End make it the lowest and the tallest; the input itself steps by single pixels, so the height is never snapped to a grid.
 * The input does not take the pointer, because its own track runs sideways and the bar is dragged up and down.
 * It is left out when the map could not be drawn, because there is nothing to stretch.
 */
export function MapResizeHandle() {
  const { t } = useTranslation();
  const { resize } = useMap();
  const [span, setSpan] = useState<MapSpan | null>(null);
  const drag = useRef<{ pointerId: number; startY: number; startHeight: number; span: MapSpan } | null>(null);

  useEffect(() => resize?.watchSpan(setSpan), [resize]);

  if (resize === null) {
    return null;
  }

  const apply = (height: number, within: MapSpan) => {
    resize.setHeight(Math.min(within.max, Math.max(within.min, height)));
  };

  const startDrag = (event: PointerEvent<HTMLDivElement>) => {
    const current = resize.readSpan();
    if (current === null) {
      return;
    }
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { pointerId: event.pointerId, startY: event.clientY, startHeight: current.height, span: current };
  };

  const moveDrag = (event: PointerEvent<HTMLDivElement>) => {
    const current = drag.current;
    if (current === null || current.pointerId !== event.pointerId) {
      return;
    }
    apply(current.startHeight + event.clientY - current.startY, current.span);
  };

  const endDrag = () => {
    drag.current = null;
  };

  const moveByKey = (event: KeyboardEvent<HTMLInputElement>) => {
    const current = resize.readSpan();
    if (current === null) {
      return;
    }
    const targets: Record<string, number> = {
      ArrowUp: current.height + KEY_STEP_PX,
      ArrowRight: current.height + KEY_STEP_PX,
      ArrowDown: current.height - KEY_STEP_PX,
      ArrowLeft: current.height - KEY_STEP_PX,
      Home: current.min,
      End: current.max,
    };
    const target = targets[event.key];
    if (target === undefined) {
      return;
    }
    event.preventDefault();
    apply(target, current);
  };

  const changeByInput = (event: ChangeEvent<HTMLInputElement>) => {
    const current = resize.readSpan();
    if (current !== null) {
      apply(Number(event.target.value), current);
    }
  };

  return (
    <div
      onPointerDown={startDrag}
      onPointerMove={moveDrag}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      className="absolute top-0 left-1/2 z-[1] flex h-[22px] w-20 -translate-x-1/2 cursor-ns-resize touch-none items-start justify-center pt-[7px] rounded-control select-none has-[:focus-visible]:outline-[3px] has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-shell"
    >
      <span aria-hidden="true" className="h-1 w-9 rounded-[2px] bg-line" />
      {span !== null ? (
        <input
          type="range"
          aria-label={t("map.resize")}
          min={Math.round(span.min)}
          max={Math.round(span.max)}
          step={1}
          value={Math.round(span.height)}
          onKeyDown={moveByKey}
          onChange={changeByInput}
          className="pointer-events-none absolute inset-0 size-full appearance-none opacity-0 outline-none"
        />
      ) : null}
    </div>
  );
}
