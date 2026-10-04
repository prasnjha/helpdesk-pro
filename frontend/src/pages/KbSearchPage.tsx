// GET /api/kb/articles?q= — search over title/body, list titles
// (component-map.md, E5-S2 AC-01). Laid out after knowledge-base.png: page
// header, a search card, then a grid of article cards.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { KbArticleSummary } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { getRole } from "../state/session";
import { formatDate } from "../utils/format";

function KbArticleCard({ article }: { article: KbArticleSummary }): JSX.Element {
  return (
    <li className="card kb-card">
      {article.tags.length > 0 && (
        <span className="tag-list">
          {article.tags.map((tag) => (
            <span key={tag} className="chip chip-open">
              {tag}
            </span>
          ))}
        </span>
      )}
      <Link to={`/kb/${article.id}`} className="kb-card-title">
        {article.title}
      </Link>
      <p className="kb-card-meta">
        <Icon name="clock" size={16} />
        Updated {formatDate(article.updated_at)}
      </p>
    </li>
  );
}

function KbSearchBox({ value, onChange }: { value: string; onChange: (q: string) => void }): JSX.Element {
  return (
    <div className="card kb-search-card">
      <label htmlFor="kb-search" className="sr-only">
        Search
      </label>
      <div className="search-input">
        <Icon name="search" />
        <input
          id="kb-search"
          type="search"
          placeholder="Search articles by title or content…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    </div>
  );
}

export function KbSearchPage(): JSX.Element {
  const [q, setQ] = useState("");
  const [articles, setArticles] = useState<KbArticleSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const isStaff = getRole() === "agent" || getRole() === "admin";

  useEffect(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    const query = params.toString();
    apiRequest<KbArticleSummary[]>(`/api/kb/articles${query ? `?${query}` : ""}`)
      .then(setArticles)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load knowledge base articles.");
      })
      .finally(() => setLoaded(true));
  }, [q]);

  return (
    <main>
      <div className="page-header">
        <div className="page-heading">
          <h1>Knowledge base</h1>
          <p className="page-lead">Answers and fixes published from resolved support tickets.</p>
        </div>
        {/* No editor controls for a customer (E5-S2 AC-03). */}
        {isStaff && (
          <Link to="/agent/kb/new" className="btn">
            <Icon name="plus" size={18} />
            New article
          </Link>
        )}
      </div>
      <ErrorBanner message={error} />
      <KbSearchBox value={q} onChange={setQ} />

      <ul className="kb-grid">
        {articles.map((article) => (
          <KbArticleCard key={article.id} article={article} />
        ))}
      </ul>
      {loaded && articles.length === 0 && !error && (
        <div className="card empty-state">
          <Icon name="book" size={28} />
          <p>No articles match your search.</p>
        </div>
      )}
    </main>
  );
}
