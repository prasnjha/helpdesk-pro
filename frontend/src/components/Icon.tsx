// Small inline stroke-icon set (24px grid, 1.75 stroke). Decorative only:
// every icon is aria-hidden, so accessible names always come from visible
// text next to it (DESIGN.md Section 5).

const PATHS = {
  inbox: "M4 13h4l1.5 3h5L16 13h4M4 13l2.5-7.5A1 1 0 0 1 7.45 5h9.1a1 1 0 0 1 .95.5L20 13v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z",
  ticket: "M4 7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v3a2 2 0 0 0 0 4v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-3a2 2 0 0 0 0-4zM10 6v12",
  plus: "M12 5v14M5 12h14",
  book: "M4 5.5A1.5 1.5 0 0 1 5.5 4H11v15H5.5A1.5 1.5 0 0 1 4 17.5zM20 5.5A1.5 1.5 0 0 0 18.5 4H13v15h5.5a1.5 1.5 0 0 0 1.5-1.5z",
  chart: "M5 20V10M12 20V4M19 20v-7",
  timer: "M12 8v5l3 2M9 2h6M12 22a8 8 0 1 0 0-16 8 8 0 0 0 0 16z",
  logout: "M15 4h3a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-3M10 16l-4-4 4-4M6 12h10",
  menu: "M4 7h16M4 12h16M4 17h16",
  close: "M6 6l12 12M18 6L6 18",
  chevronRight: "M9 6l6 6-6 6",
  arrowLeft: "M19 12H5M11 6l-6 6 6 6",
  clock: "M12 7v5l3 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z",
  lock: "M7 11V8a5 5 0 0 1 10 0v3M6 11h12v9H6z",
  alert: "M12 8v5M12 16.5v.5M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z",
  check: "M5 12.5l4.5 4.5L19 7.5",
  search: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4",
  flag: "M5 21V4M5 4h11l-2 4 2 4H5",
  history: "M3 12a9 9 0 1 0 3-6.7M3 4v4h4M12 8v4l3 2",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 20a8 8 0 0 1 16 0",
  filter: "M4 6h16M7 12h10M10 18h4",
  edit: "M4 20h4L19 9l-4-4L4 16zM14 6l4 4",
  trash: "M5 7h14M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3",
  send: "M4 12l16-8-6 16-2.5-6.5z",
  note: "M6 4h9l4 4v12H6zM14 4v5h5M9 13h6M9 17h4",
} as const;

export type IconName = keyof typeof PATHS;

interface IconProps {
  name: IconName;
  size?: number;
  className?: string;
}

export function Icon({ name, size = 20, className }: IconProps): JSX.Element {
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      className={className ? `icon ${className}` : "icon"}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={PATHS[name]} />
    </svg>
  );
}
