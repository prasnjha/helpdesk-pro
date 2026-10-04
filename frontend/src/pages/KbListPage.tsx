// GET /api/kb/articles?q=&tag= — search over title/body, list titles
// (component-map.md, E5-S2 AC-01).

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { KbArticleSummary } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { getRole } from "../state/session";

export function KbListPage(): JSX.Element {
  const [q, setQ] = useState("");
  const [articles, setArticles] = useState<KbArticleSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const isStaff = getRole() === "agent" || getRole() === "admin";

  useEffect(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    const query = params.toString();
    apiRequest<KbArticleSummary[]>(`/api/kb/articles${query ? `?${query}` : ""}`)
      .then(setArticles)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load knowledge base articles.");
      });
  }, [q]);

  return (
    <main>
      <h1>Knowledge base</h1>
      <ErrorBanner message={error} />

      <label htmlFor="kb-search">Search</label>
      <input id="kb-search" value={q} onChange={(e) => setQ(e.target.value)} />

      {/* No editor controls for a customer (E5-S2 AC-03). */}
      {isStaff && <Link to="/kb/new">New article</Link>}

      <ul>
        {articles.map((article) => (
          <li key={article.id}>
            <Link to={`/kb/${article.id}`}>{article.title}</Link>
            {article.tags.length > 0 && <span> ({article.tags.join(", ")})</span>}
          </li>
        ))}
      </ul>
    </main>
  );
}
