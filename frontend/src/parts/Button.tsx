import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Link } from "react-router";

import { Icon } from "./Icon.tsx";
import type { IconName } from "./iconPaths.ts";

type ButtonLook = "outline" | "primary" | "cta" | "link";

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className"> {
  look?: ButtonLook;
  isSmall?: boolean;
  icon?: IconName;
  to?: string;
  className?: string;
  children: ReactNode;
}

const BASE = "inline-flex items-center justify-center gap-1.5 rounded-panel border-[1.5px] font-bold no-underline";

const LOOKS: Record<Exclude<ButtonLook, "link">, string> = {
  outline: "border-shell bg-transparent text-shell",
  primary: "border-shell bg-shell text-white",
  cta: "border-yellow bg-yellow text-ink",
};

const OFF = "disabled:cursor-not-allowed disabled:border-line disabled:bg-off disabled:text-off-ink";

const LINK = "inline-flex min-h-11 items-center gap-1.5 px-0.5 text-[14px] font-semibold text-shell underline underline-offset-[3px]";

/**
 * A button of the interface in one of its looks: outlined, primary, the yellow call to action, or a text link.
 * With an address it is a link to another view and keeps the same look, its identifier and its accessible names.
 * The small size is narrower and has smaller letters, and it keeps the height of 44 px a finger needs.
 */
export function Button({ look = "outline", isSmall = false, icon, to, className = "", children, type = "button", ...rest }: ButtonProps) {
  const size = isSmall ? "min-h-11 px-3 text-[13px]" : "min-h-[46px] px-4 text-[14.5px]";
  const classes = look === "link" ? `${LINK} ${className}` : `${BASE} ${size} ${LOOKS[look]} ${OFF} ${className}`;
  const content = (
    <>
      {icon !== undefined ? <Icon name={icon} /> : null}
      {children}
    </>
  );
  if (to !== undefined) {
    return (
      <Link to={to} id={rest.id} aria-label={rest["aria-label"]} aria-describedby={rest["aria-describedby"]} aria-current={rest["aria-current"]} className={classes}>
        {content}
      </Link>
    );
  }
  return (
    <button type={type} className={classes} {...rest}>
      {content}
    </button>
  );
}
