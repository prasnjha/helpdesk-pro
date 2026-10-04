// Article detail and the agent/admin editor (component-map.md, E5-S2
// AC-02/03). `id === "new"` renders the create form (POST, fed a
// `source_ticket_id` query param from the ticket detail's publish link);
// an existing id renders the detail view with Edit/Delete for staff and
// read-only prose for a customer — no editor controls at all.

import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { KbArticle } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { getRole } from "../state/session";

export function KbArticlePage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const isStaff = getRole() === "agent" || getRole() === "admin";
  const isNew = id === "new";

  const [article, setArticle] = useState<KbArticle | null>(null);
  const [editing, setEditing] = useState(isNew);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isNew || !id) return;
    setEditing(false);
    apiRequest<KbArticle>(`/api/kb/articles/${id}`)
      .then((a) => {
        setArticle(a);
        setTitle(a.title);
        setBody(a.body);
        setTags(a.tags.join(", "));
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load this article.");
      });
  }, [id, isNew]);

  function parsedTags(): string[] {
    return tags
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);
  }

  function handleSave(event: React.FormEvent): void {
    event.preventDefault();
    setError(null);
    if (isNew) {
      const sourceTicketId = searchParams.get("source_ticket_id") ?? "";
      apiRequest<KbArticle>("/api/kb/articles", {
        method: "POST",
        body: { source_ticket_id: sourceTicketId, title, body, tags: parsedTags() },
      })
        .then((created) => navigate(`/kb/${created.id}`))
        .catch((err: unknown) => {
          setError(err instanceof ApiError ? err.message : "Unable to publish this article.");
        });
      return;
    }
    if (!id) return;
    apiRequest<KbArticle>(`/api/kb/articles/${id}`, {
      method: "PUT",
      body: { title, body, tags: parsedTags() },
    })
      .then((updated) => {
        setArticle(updated);
        setTags(updated.tags.join(", "));
        setEditing(false);
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to save this article.");
      });
  }

  function handleDelete(): void {
    if (!id) return;
    setError(null);
    apiRequest<void>(`/api/kb/articles/${id}`, { method: "DELETE" })
      .then(() => navigate("/kb"))
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to delete this article.");
      });
  }

  if (!isNew && !article) {
    return (
      <main>
        <ErrorBanner message={error} />
      </main>
    );
  }

  if (editing) {
    return (
      <main>
        <h1>{isNew ? "New article" : "Edit article"}</h1>
        <ErrorBanner message={error} />
        <form onSubmit={handleSave}>
          <label htmlFor="article-title">Title</label>
          <input id="article-title" value={title} onChange={(e) => setTitle(e.target.value)} />

          <label htmlFor="article-body">Body</label>
          <textarea id="article-body" value={body} onChange={(e) => setBody(e.target.value)} />

          <label htmlFor="article-tags">Tags (comma separated)</label>
          <input id="article-tags" value={tags} onChange={(e) => setTags(e.target.value)} />

          <button type="submit">Save</button>
        </form>
      </main>
    );
  }

  return (
    <main>
      <h1>{article?.title}</h1>
      <ErrorBanner message={error} />
      <p>{article?.body}</p>
      <p data-testid="article-tags">{article?.tags.join(", ")}</p>

      {isStaff && (
        <>
          <button type="button" onClick={() => setEditing(true)}>
            Edit
          </button>
          <button type="button" onClick={handleDelete}>
            Delete
          </button>
        </>
      )}
    </main>
  );
}
