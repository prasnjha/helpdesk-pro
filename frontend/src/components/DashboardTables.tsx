// open_by_queue, breached_by_priority and escalations_in_period as tables
// (component-map.md: AdminDashboardPage; E6-S2, AC-10's UI). Each table sits
// in its own Level-1 card (DESIGN.md 5.4).

import type { DashboardReport } from "../api/types";
import { PriorityBadge } from "./PriorityBadge";

interface DashboardTablesProps {
  dashboard: DashboardReport;
}

export function DashboardTables({ dashboard }: DashboardTablesProps): JSX.Element {
  return (
    <div className="dashboard-grid">
      <div className="card table-card">
        <div className="card-header">
          <h3 className="card-title">Open tickets by queue</h3>
        </div>
        <table data-testid="open-by-queue-table" className="data-table">
          <thead>
            <tr>
              <th>Queue</th>
              <th className="num">Count</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.open_by_queue.map((row) => (
              <tr key={row.queue.slug}>
                <td>{row.queue.name}</td>
                <td className="num">{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card table-card">
        <div className="card-header">
          <h3 className="card-title">Breached tickets by priority</h3>
        </div>
        <table data-testid="breached-by-priority-table" className="data-table">
          <thead>
            <tr>
              <th>Priority</th>
              <th className="num">Count</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.breached_by_priority.map((row) => (
              <tr key={row.priority}>
                <td>
                  <PriorityBadge priority={row.priority} />
                </td>
                <td className="num">{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card table-card">
        <div className="card-header">
          <h3 className="card-title">Escalations in period</h3>
        </div>
        <table data-testid="escalations-in-period-table" className="data-table">
          <thead>
            <tr>
              <th>Escalations in period</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="stat-value">{dashboard.escalations_in_period}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
