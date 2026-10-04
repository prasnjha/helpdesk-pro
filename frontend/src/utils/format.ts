// Display-only formatting of API timestamps. Always UTC so the rendered text
// does not depend on the viewer's (or the CI runner's) timezone.

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function parse(value: string): Date | null {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

export function formatDate(value: string): string {
  const date = parse(value);
  if (!date) return value;
  return `${date.getUTCDate()} ${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()}`;
}

export function formatDateTime(value: string): string {
  const date = parse(value);
  if (!date) return value;
  return `${formatDate(value)}, ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())} UTC`;
}
