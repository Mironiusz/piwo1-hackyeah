/**
 * Moves the keyboard focus to the map, so the arrow keys move it under the mark of a view that picks a point.
 * The layout of the map views offers no way to focus the map, so the map is found by the class name the map library gives its canvas.
 */
export function focusMap(): void {
  document.querySelector<HTMLElement>(".maplibregl-canvas")?.focus();
}
