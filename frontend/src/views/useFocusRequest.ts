import { useCallback, useEffect, useState } from "react";

interface FocusRequest {
  id: string;
  onlyWhenLost: boolean;
}

/**
 * Returns the function a view calls to move the keyboard focus to an element by its identifier, once the view is drawn again.
 * A view needs it after an action that removed or switched off the element that held the focus, so a person
 * with a keyboard or a screen reader does not start again from the top of the page.
 * With onlyWhenLost the focus moves only when no element holds it, so a person who moved on in the meantime is left alone.
 */
export function useFocusRequest(): (id: string, onlyWhenLost?: boolean) => void {
  const [request, setRequest] = useState<FocusRequest | null>(null);

  useEffect(() => {
    if (request === null) {
      return;
    }
    const isFocusLost = document.activeElement === null || document.activeElement === document.body;
    if (!request.onlyWhenLost || isFocusLost) {
      document.getElementById(request.id)?.focus();
    }
  }, [request]);

  return useCallback((id: string, onlyWhenLost = false) => {
    setRequest({ id, onlyWhenLost });
  }, []);
}
