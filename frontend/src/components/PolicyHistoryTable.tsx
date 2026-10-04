// Versions for one priority, newest first (component-map.md:
// AdminPoliciesPage; E6-S2). Sorting is the caller's responsibility; every
// published version is immutable so there is nothing to edit here.

import type { Priority, SlaPolicyVersion } from "../api/types";

interface PolicyHistoryTableProps {
  priority: Priority;
  rows: SlaPolicyVersion[];
}

export function PolicyHistoryTable({ priority, rows }: PolicyHistoryTableProps): JSX.Element {
  return (
    <div>
      <h3>{priority}</h3>
      <table>
        <thead>
          <tr>
            <th>Version</th>
            <th>Response</th>
            <th>Resolution</th>
            <th>Published</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} data-testid={`policy-row-${priority}`}>
              <td>{row.version}</td>
              <td>{row.response_minutes}</td>
              <td>{row.resolution_minutes}</td>
              <td>{row.published_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
