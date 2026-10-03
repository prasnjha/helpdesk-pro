// Shows error.message from the error envelope (frontend/CLAUDE.md).

interface ErrorBannerProps {
  message: string | null;
}

export function ErrorBanner({ message }: ErrorBannerProps): JSX.Element | null {
  if (!message) return null;
  return (
    <div role="alert" className="error-banner">
      {message}
    </div>
  );
}
