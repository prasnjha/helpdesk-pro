// GET /api/kb/articles/{id} — read-only detail view (component-map.md,
// E5-S2 AC-02). Edit and Delete for staff link to KbEditorPage; a customer
// sees no editor controls at all.

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { KbArticle } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { getRole } from "../state/session";

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

  if (!article) {
    return (
      <main>
        <ErrorBanner message={error} />
      </main>
    );
  }

  return (
    <main>
      <h1>{article.title}</h1>
      <ErrorBanner message={error} />
      <p>{article.body}</p>
      <p data-testid="article-tags">{article.tags.join(", ")}</p>

      {isStaff && (
        <>
          <Link to={`/agent/kb/${article.id}/edit`}>Edit</Link>
          <button type="button" onClick={handleDelete}>
            Delete
          </button>
        </>
      )}
    </main>
  );
}
