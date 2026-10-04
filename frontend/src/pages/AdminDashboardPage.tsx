// Operational dashboard: open_by_queue, breached_by_priority and
// escalations_in_period (component-map.md, E6-S2 AC-10's UI). No mockup:
// styled after admin-console.png's shell and table cards.

import { useEffect, useState } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { DashboardReport } from "../api/types";
import { AdminPageHeading } from "../components/AdminPageHeading";
import { DashboardTables } from "../components/DashboardTables";
import { ErrorBanner } from "../components/ErrorBanner";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function AdminDashboardPage(): JSX.Element {
  const [dashboard, setDashboard] = useState<DashboardReport | null>(null);
  const [from, setFrom] = useState(todayIso());
  const [to, setTo] = useState(todayIso());
  const [error, setError] = useState<string | null>(null);

  function loadDashboard(): void {
    apiRequest<DashboardReport>(`/api/admin/dashboard?from=${from}&to=${to}`)
      .then(setDashboard)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load the dashboard.");
      });
  }

  useEffect(() => {
    loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main>
      <AdminPageHeading lead="Open, breached and escalated tickets for a reporting period." />
      <ErrorBanner message={error} />

      <section aria-label="Dashboard" className="admin-section">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Dashboard</h2>
          </div>
          <div className="inline-form dashboard-period">
            <div className="field">
              <label htmlFor="dashboard-from">From</label>
              <input id="dashboard-from" value={from} onChange={(e) => setFrom(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="dashboard-to">To</label>
              <input id="dashboard-to" value={to} onChange={(e) => setTo(e.target.value)} />
            </div>
            <button type="button" onClick={loadDashboard}>
              Refresh
            </button>
          </div>
        </div>

        {dashboard && <DashboardTables dashboard={dashboard} />}
      </section>
    </main>
  );
}
