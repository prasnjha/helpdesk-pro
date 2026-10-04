// POST and PUT /api/kb/articles (component-map.md, E5-S2). `id === undefined`
// (route /agent/kb/new) renders the create form, fed a `source_ticket_id`
// query param from the ticket detail's publish link; /agent/kb/:id/edit
// loads the existing article. `source_ticket_id` is read-only.

import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { KbArticle } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";

export function KbEditorPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const isNew = id === undefined;

  const [sourceTicketId, setSourceTicketId] = useState(searchParams.get("source_ticket_id") ?? "");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isNew || !id) return;
    apiRequest<KbArticle>(`/api/kb/articles/${id}`)
      .then((a) => {
        setTitle(a.title);
        setBody(a.body);
        setTags(a.tags.join(", "));
        setSourceTicketId(a.source_ticket_id);
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
      .then((updated) => navigate(`/kb/${updated.id}`))
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to save this article.");
      });
  }

  return (
    <main>
      <h1>{isNew ? "New article" : "Edit article"}</h1>
      <ErrorBanner message={error} />
      <form onSubmit={handleSave}>
        <label htmlFor="article-source-ticket">Source ticket</label>
        <input id="article-source-ticket" value={sourceTicketId} readOnly />

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
