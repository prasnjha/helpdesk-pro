// open_by_queue, breached_by_priority and escalations_in_period as tables
// (component-map.md: AdminDashboardPage; E6-S2, AC-10's UI).

import type { DashboardReport } from "../api/types";

interface DashboardTablesProps {
  dashboard: DashboardReport;
}

export function DashboardTables({ dashboard }: DashboardTablesProps): JSX.Element {
  return (
    <>
      <h3>Open tickets by queue</h3>
      <table data-testid="open-by-queue-table">
        <thead>
          <tr>
            <th>Queue</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          {dashboard.open_by_queue.map((row) => (
            <tr key={row.queue.slug}>
              <td>{row.queue.name}</td>
              <td>{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Breached tickets by priority</h3>
      <table data-testid="breached-by-priority-table">
        <thead>
          <tr>
            <th>Priority</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          {dashboard.breached_by_priority.map((row) => (
            <tr key={row.priority}>
              <td>{row.priority}</td>
              <td>{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Escalations in period</h3>
      <table data-testid="escalations-in-period-table">
        <thead>
          <tr>
            <th>Escalations in period</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{dashboard.escalations_in_period}</td>
          </tr>
        </tbody>
      </table>
    </>
  );
}
