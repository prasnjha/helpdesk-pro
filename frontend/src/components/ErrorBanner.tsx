// Shows error.message from the error envelope (frontend/CLAUDE.md), styled
// as the critical tint banner (DESIGN.md 1.1 critical-bg / critical-border).

import { Icon } from "./Icon";

interface ErrorBannerProps {
  message: string | null;
}

export function ErrorBanner({ message }: ErrorBannerProps): JSX.Element | null {
  if (!message) return null;
  return (
    <div role="alert" className="banner banner-critical error-banner">
      <Icon name="alert" />
      <span>{message}</span>
    </div>
  );
}
