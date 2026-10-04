// SLA policy editor with version history (component-map.md, E6-S2
// AC-01/02).

import { useEffect, useState } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { Priority, SlaPolicyVersion } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { PolicyEditor } from "../components/PolicyEditor";
import { PolicyHistoryTable } from "../components/PolicyHistoryTable";

const PRIORITIES: Priority[] = ["Critical", "High", "Medium", "Low"];

export function AdminPoliciesPage(): JSX.Element {
  const [versions, setVersions] = useState<SlaPolicyVersion[]>([]);
  const [priority, setPriority] = useState<Priority>("High");
  const [responseMinutes, setResponseMinutes] = useState("60");
  const [resolutionMinutes, setResolutionMinutes] = useState("480");
  const [error, setError] = useState<string | null>(null);

  function loadVersions(): void {
    apiRequest<SlaPolicyVersion[]>("/api/admin/sla-policies")
      .then(setVersions)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load SLA policy versions.");
      });
  }

  useEffect(() => {
    loadVersions();
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
        <PolicyEditor
          priority={priority}
          priorities={PRIORITIES}
          onPriorityChange={setPriority}
          responseMinutes={responseMinutes}
          onResponseMinutesChange={setResponseMinutes}
          resolutionMinutes={resolutionMinutes}
          onResolutionMinutesChange={setResolutionMinutes}
          onSubmit={handleSavePolicy}
        />

        {versionsByPriority.map(({ priority: p, rows }) => (
          <PolicyHistoryTable key={p} priority={p} rows={rows} />
        ))}
      </section>
    </main>
  );
}
