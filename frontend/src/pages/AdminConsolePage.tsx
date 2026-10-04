// SLA policy editor with version history, and the dashboard tables
// (component-map.md, E6-S2 AC-01/02/03, AC-10's UI).

import { useEffect, useState } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { DashboardReport, Priority, SlaPolicyVersion } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";

const PRIORITIES: Priority[] = ["Critical", "High", "Medium", "Low"];

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function AdminConsolePage(): JSX.Element {
  const [versions, setVersions] = useState<SlaPolicyVersion[]>([]);
  const [priority, setPriority] = useState<Priority>("High");
  const [responseMinutes, setResponseMinutes] = useState("60");
  const [resolutionMinutes, setResolutionMinutes] = useState("480");
  const [dashboard, setDashboard] = useState<DashboardReport | null>(null);
  const [from, setFrom] = useState(todayIso());
  const [to, setTo] = useState(todayIso());
  const [error, setError] = useState<string | null>(null);

  function loadVersions(): void {
    apiRequest<SlaPolicyVersion[]>("/api/admin/sla-policies")
      .then(setVersions)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load SLA policy versions.");
      });
  }

  function loadDashboard(): void {
    apiRequest<DashboardReport>(`/api/admin/dashboard?from=${from}&to=${to}`)
      .then(setDashboard)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load the dashboard.");
      });
  }

  useEffect(() => {
    loadVersions();
    loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSavePolicy(event: React.FormEvent): void {
    event.preventDefault();
    setError(null);
    apiRequest<SlaPolicyVersion>("/api/admin/sla-policies", {
      method: "POST",
      body: {
        priority,
        response_minutes: Number(responseMinutes),
        resolution_minutes: Number(resolutionMinutes),
      },
    })
      .then(() => loadVersions())
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to save the policy.");
      });
  }

  // Version history is newest first per priority, and every published
  // version is immutable (PATCH/PUT/DELETE always 409), so edit controls
  // are never rendered — there is nothing to toggle (E6-S2 AC-02).
  const versionsByPriority = PRIORITIES.map((p) => ({
    priority: p,
    rows: versions.filter((v) => v.priority === p).sort((a, b) => b.version - a.version),
  }));

  return (
    <main>
      <h1>Admin console</h1>
      <ErrorBanner message={error} />

      <section aria-label="SLA policy editor">
        <h2>SLA policy editor</h2>
        <form onSubmit={handleSavePolicy}>
          <label htmlFor="policy-priority">Priority</label>
          <select
            id="policy-priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          <label htmlFor="policy-response">Response minutes</label>
          <input
            id="policy-response"
            value={responseMinutes}
            onChange={(e) => setResponseMinutes(e.target.value)}
          />

          <label htmlFor="policy-resolution">Resolution minutes</label>
          <input
            id="policy-resolution"
            value={resolutionMinutes}
            onChange={(e) => setResolutionMinutes(e.target.value)}
          />

          <button type="submit">Save new version</button>
        </form>

        {versionsByPriority.map(({ priority: p, rows }) => (
          <div key={p}>
            <h3>{p}</h3>
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
                  <tr key={row.id} data-testid={`policy-row-${p}`}>
                    <td>{row.version}</td>
                    <td>{row.response_minutes}</td>
                    <td>{row.resolution_minutes}</td>
                    <td>{row.published_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </section>

      <section aria-label="Dashboard">
        <h2>Dashboard</h2>
        <label htmlFor="dashboard-from">From</label>
        <input id="dashboard-from" value={from} onChange={(e) => setFrom(e.target.value)} />
        <label htmlFor="dashboard-to">To</label>
        <input id="dashboard-to" value={to} onChange={(e) => setTo(e.target.value)} />
        <button type="button" onClick={loadDashboard}>
          Refresh
        </button>

        {dashboard && (
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

            <p>Escalations in period: {dashboard.escalations_in_period}</p>
          </>
        )}
      </section>
    </main>
  );
}
