// Level-1 surface (DESIGN.md Section 5.4): white, 1 px border, 16 px radius,
// 24 px padding. Optional header with a title and right-aligned actions.

import type { ReactNode } from "react";

interface CardProps {
  title?: ReactNode;
  actions?: ReactNode;
  ariaLabel?: string;
  className?: string;
  children: ReactNode;
}

export function Card({ title, actions, ariaLabel, className, children }: CardProps): JSX.Element {
  const classes = className ? `card ${className}` : "card";
  return (
    <section className={classes} aria-label={ariaLabel}>
      {(title || actions) && (
        <div className="card-header">
          {title && <h2 className="card-title">{title}</h2>}
          {actions && <div className="card-actions">{actions}</div>}
        </div>
      )}
      {children}
    </section>
  );
}
