import { useCallback, useEffect, useRef } from "react";

/**
 * Returns the function that tells whether the step is still on the screen.
 * A step asks it after a request, so an answer that arrives after the person left the flow leads nowhere.
 */
export function useIsMounted(): () => boolean {
  const isMounted = useRef(false);
  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);
  return useCallback(() => isMounted.current, []);
}
