// Button variants from DESIGN.md Section 5.1. `danger` is reserved for
// permanent, destructive actions (deleting a KB article).

import type { ButtonHTMLAttributes } from "react";

export type ButtonVariant = "primary" | "secondary" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: "md" | "sm";
}

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: "",
  secondary: "btn-secondary",
  danger: "btn-danger",
};

export function buttonClass(variant: ButtonVariant = "primary", size: "md" | "sm" = "md"): string {
  return ["btn", VARIANT_CLASS[variant], size === "sm" ? "btn-sm" : ""].filter(Boolean).join(" ");
}

export function Button({
  variant = "primary",
  size = "md",
  type = "button",
  className,
  ...rest
}: ButtonProps): JSX.Element {
  const classes = [buttonClass(variant, size), className].filter(Boolean).join(" ");
  return <button type={type} className={classes} {...rest} />;
}
