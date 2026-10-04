import { Component, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { Button } from "../parts/Button.tsx";
import { Note } from "../parts/Note.tsx";

/**
 * What a person sees in place of a view that failed: the plain text and the way to try again.
 */
function Failure({ onRetry }: { onRetry: () => void }) {
  const { t } = useTranslation();
  return (
    <div className="flex-1 bg-surface px-4 py-[18px]">
      <Note kind="strong" announce="alert">
        <p>{t("state.failed")}</p>
      </Note>
      <div className="mt-4">
        <Button onClick={onRetry}>{t("action.retry")}</Button>
      </div>
    </div>
  );
}

interface ErrorBoundaryProps {
  resetKey: string;
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasFailed: boolean;
  resetKey: string;
}

/**
 * The one safety net around the views. An answer of the service that the code cannot use, and any other failure
 * while a view is drawn, ends in a plain text instead of an empty page. A change of the reset key, the address of the view,
 * lets the next view be drawn again.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasFailed: false, resetKey: this.props.resetKey };

  static getDerivedStateFromError(): Partial<ErrorBoundaryState> {
    return { hasFailed: true };
  }

  static getDerivedStateFromProps(props: ErrorBoundaryProps, state: ErrorBoundaryState): ErrorBoundaryState | null {
    return props.resetKey === state.resetKey ? null : { hasFailed: false, resetKey: props.resetKey };
  }

  render(): ReactNode {
    if (this.state.hasFailed) {
      return <Failure onRetry={() => this.setState({ hasFailed: false })} />;
    }
    return this.props.children;
  }
}
