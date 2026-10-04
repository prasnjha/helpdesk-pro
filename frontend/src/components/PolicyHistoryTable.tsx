// Versions for one priority, newest first (component-map.md:
// AdminPoliciesPage; E6-S2). Sorting is the caller's responsibility; every
// published version is immutable so there is nothing to edit here.

import type { Priority, SlaPolicyVersion } from "../api/types";
import { formatDateTime } from "../utils/format";
import { Icon } from "./Icon";

interface PolicyHistoryTableProps {
  priority: Priority;
  rows: SlaPolicyVersion[];
}

export function PolicyHistoryTable({ priority, rows }: PolicyHistoryTableProps): JSX.Element {
  return (
    <div className={`card table-card policy-history notch-card notch-${priority.toLowerCase()}`}>
      <div className="card-header">
        <h3 className="card-title">{priority}</h3>
        <span className="chip chip-closed">
          <Icon name="lock" size={12} />
          Published, read-only
        </span>
      </div>
      <div className="table-scroll">
        <table className="data-table">
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
                <td>
                  <span className="version-pill">{row.version}</span>
                </td>
                <td className="num">{row.response_minutes} min</td>
                <td className="num">{row.resolution_minutes} min</td>
                <td className="muted">{formatDateTime(row.published_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
