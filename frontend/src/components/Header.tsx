// Shared header: logo + product name (DESIGN.md Section 5.6 nav anchors,
// frontend/CLAUDE.md "the logo ... for the header and login page").

export function Header(): JSX.Element {
  return (
    <header className="app-header">
      <img src="/helpdesk-pro-logo.png" alt="HelpDesk Pro" className="app-header-logo" />
      <span className="app-header-name">HelpDesk Pro</span>
    </header>
  );
}
