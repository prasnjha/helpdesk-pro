// GET /api/kb/articles/{id} — read-only detail view (component-map.md,
// E5-S2 AC-02). Edit and Delete for staff link to KbEditorPage; a customer
// sees no editor controls at all. Laid out after
// article-detail-cisco-anyconnect-vpn.png: back link, header card, body card.

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { KbArticle } from "../api/types";
import { BackLink } from "../components/BackLink";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { getRole } from "../state/session";
import { formatDate } from "../utils/format";

interface ArticleHeaderProps {
  article: KbArticle;
  isStaff: boolean;
  onDelete: () => void;
}

function ArticleHeader({ article, isStaff, onDelete }: ArticleHeaderProps): JSX.Element {
  return (
    <div className="card kb-article-header">
      <div className="kb-article-top">
        <div data-testid="article-tags" className="tag-list">
          {article.tags.map((tag) => (
            <span key={tag} className="chip chip-open">
              {tag}
            </span>
          ))}
        </div>
        {isStaff && (
          <div className="card-actions">
            <Link to={`/agent/kb/${article.id}/edit`} className="btn btn-secondary btn-sm">
              <Icon name="edit" size={16} />
              Edit
            </Link>
            <button type="button" className="btn-danger btn-sm" onClick={onDelete}>
              <Icon name="trash" size={16} />
              Delete
            </button>
          </div>
        )}
      </div>
      <h1>{article.title}</h1>
      <p className="kb-article-meta">
        <span>
          <Icon name="clock" size={16} />
          Last updated {formatDate(article.updated_at)}
        </span>
        <span>
          <Icon name="ticket" size={16} />
          Source ticket <span className="code-chip">{article.source_ticket_id}</span>
        </span>
      </p>
    </div>
  );
}

export function KbArticlePage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isStaff = getRole() === "agent" || getRole() === "admin";

  const [article, setArticle] = useState<KbArticle | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    apiRequest<KbArticle>(`/api/kb/articles/${id}`)
      .then(setArticle)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load this article.");
      });
  }, [id]);

  function handleDelete(): void {
    if (!id) return;
    setError(null);
    apiRequest<void>(`/api/kb/articles/${id}`, { method: "DELETE" })
      .then(() => navigate("/kb"))
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to delete this article.");
      });
  }

  return (
    <main className="page-narrow">
      <BackLink to="/kb">Back to knowledge base</BackLink>
      <ErrorBanner message={error} />
      {article && (
        <>
          <ArticleHeader article={article} isStaff={isStaff} onDelete={handleDelete} />
          <article className="card kb-article-body">
            <p>{article.body}</p>
          </article>
        </>
      )}
    </main>
  );
}
