import { useEffect, useRef, type RefObject } from "react";

/**
 * Returns the reference of the heading of a step. The heading takes the focus when the step opens,
 * so a person with a keyboard or a screen reader starts every step at its top, and again when the key changes,
 * which a step uses when its content is replaced without a change of the address.
 */
export function useHeadingFocus(focusKey: string): RefObject<HTMLHeadingElement | null> {
  const heading = useRef<HTMLHeadingElement | null>(null);
  useEffect(() => {
    heading.current?.focus();
  }, [focusKey]);
  return heading;
}
