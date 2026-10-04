import type { ChangeEvent } from "react";
import { useTranslation } from "react-i18next";

interface FieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: "text" | "password" | "search" | "number";
  isOptional?: boolean;
  isMultiline?: boolean;
  hint?: string;
  error?: string | null;
  autoComplete?: string;
  inputMode?: "text" | "numeric" | "search";
  maxLength?: number;
  enterKeyHint?: "search" | "done" | "next" | "go";
  className?: string;
}

const INPUT = "w-full rounded-panel border-[1.5px] bg-white px-3 py-2 text-[16px] text-ink";

/**
 * A labelled text field with its hint and its error. The hint and the error are tied to the field,
 * so a screen reader reads them with it, and an error is announced when it appears.
 */
export function Field({
  id,
  label,
  value,
  onChange,
  type = "text",
  isOptional = false,
  isMultiline = false,
  hint,
  error = null,
  autoComplete,
  inputMode,
  maxLength,
  enterKeyHint,
  className = "mt-3.5",
}: FieldProps) {
  const { t } = useTranslation();
  const hintId = hint !== undefined ? `${id}-hint` : undefined;
  const errorId = error !== null ? `${id}-error` : undefined;
  const describedBy = [errorId, hintId].filter((part) => part !== undefined).join(" ") || undefined;
  const border = error !== null ? "border-barrier" : "border-field";
  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => onChange(event.target.value);

  return (
    <div className={`grid gap-[5px] ${className}`}>
      <label htmlFor={id} className="text-[13.5px] font-semibold">
        {label}
        {isOptional ? <span className="font-normal text-muted"> {t("field.optional")}</span> : null}
      </label>
      {isMultiline ? (
        <textarea
          id={id}
          value={value}
          onChange={handleChange}
          maxLength={maxLength}
          aria-invalid={error !== null}
          aria-describedby={describedBy}
          className={`${INPUT} ${border} min-h-[84px] resize-y`}
        />
      ) : (
        <input
          id={id}
          type={type}
          value={value}
          onChange={handleChange}
          autoComplete={autoComplete}
          inputMode={inputMode}
          maxLength={maxLength}
          enterKeyHint={enterKeyHint}
          aria-invalid={error !== null}
          aria-describedby={describedBy}
          className={`${INPUT} ${border} min-h-[46px]`}
        />
      )}
      {error !== null ? (
        <p id={errorId} role="alert" className="text-[13px] font-semibold text-barrier">
          {error}
        </p>
      ) : null}
      {hint !== undefined ? (
        <p id={hintId} className="text-[12.5px] text-muted">
          {hint}
        </p>
      ) : null}
    </div>
  );
}
