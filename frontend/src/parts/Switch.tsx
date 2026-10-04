interface SwitchOption<T extends string> {
  value: T;
  label: string;
}

interface SwitchProps<T extends string> {
  label?: string;
  labelledBy?: string;
  options: readonly SwitchOption<T>[];
  value: T;
  onChange: (value: T) => void;
  isOff?: boolean;
  className?: string;
}

/**
 * A choice between a few named options, drawn as joined buttons of which one is pressed.
 * The group has a name, and every button says whether it is the pressed one.
 */
export function Switch<T extends string>({ label, labelledBy, options, value, onChange, isOff = false, className = "" }: SwitchProps<T>) {
  return (
    <fieldset
      aria-label={label}
      aria-labelledby={labelledBy}
      className={`m-0 grid min-w-0 overflow-hidden rounded-panel border-[1.5px] p-0 ${isOff ? "border-line" : "border-shell"} ${className}`}
      style={{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }}
    >
      {options.map((option) => {
        const isPressed = option.value === value;
        const look = isOff ? (isPressed ? "bg-off text-off-ink" : "text-off-ink") : isPressed ? "bg-shell text-white" : "text-shell";
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={isPressed}
            disabled={isOff}
            onClick={() => onChange(option.value)}
            className={`min-h-11 px-2 text-[13.5px] font-semibold -outline-offset-[3px] disabled:cursor-not-allowed ${look} ${isPressed && !isOff ? "focus-visible:outline-yellow" : ""}`}
          >
            {option.label}
          </button>
        );
      })}
    </fieldset>
  );
}
