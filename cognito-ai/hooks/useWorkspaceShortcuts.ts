import { useEffect, useRef } from "react";

type Handlers = {
  submitAnswer?: () => void;
  goNext?: () => void;
  toggleHint?: () => void;
  selectOption?: (index: number) => void;
  enabled?: boolean;
};

// Binds global keyboard shortcuts for the workspace. Keeps handlers in a ref
// to avoid re-registering listeners on every render.
export function useWorkspaceShortcuts(handlers: Handlers) {
  const handlersRef = useRef<Handlers>(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  useEffect(() => {
    if (!handlers.enabled) return;

    function onKey(e: KeyboardEvent) {
      // ignore when focus is in a form control
      const active = document.activeElement as HTMLElement | null;
      if (active) {
        const tag = active.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || active.isContentEditable) {
          return;
        }
      }

      const h = handlersRef.current;
      const key = e.key;

      // numeric choices 1-4
      if (/^[1-4]$/.test(key)) {
        const idx = parseInt(key, 10) - 1;
        h.selectOption?.(idx);
        e.preventDefault();
        return;
      }

      // Enter => submit if available, otherwise goNext
      if (key === "Enter") {
        if (h.submitAnswer) {
          try {
            h.submitAnswer();
          } catch {}
        } else {
          h.goNext?.();
        }
        e.preventDefault();
        return;
      }

      // H => hint
      if (key.toLowerCase() === "h") {
        h.toggleHint?.();
        e.preventDefault();
        return;
      }
    }

    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [handlers.enabled]);
}
