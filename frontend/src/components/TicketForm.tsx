// Title, description, category, priority; client-side empty-title check sends
// no request (component-map.md, E2-S4).

import { useState } from "react";

import type { Category, CreateTicketRequest, Priority } from "../api/types";

interface TicketFormProps {
  onSubmit: (payload: CreateTicketRequest) => void | Promise<void>;
}

const CATEGORIES: Category[] = ["Billing", "Technical", "Account"];
const PRIORITIES: Priority[] = ["Critical", "High", "Medium", "Low"];

export function TicketForm({ onSubmit }: TicketFormProps): JSX.Element {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<Category>("Billing");
  const [priority, setPriority] = useState<Priority>("Medium");
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  function handleSubmit(event: React.FormEvent): void {
    event.preventDefault();
    if (title.trim().length === 0) {
      setValidationMessage("Title is required.");
      return;
    }
    setValidationMessage(null);
    void onSubmit({ title, description, category, priority });
  }

  const titleInvalid = validationMessage !== null;

  return (
    <form onSubmit={handleSubmit} className="ticket-form">
      <div className="form-row">
        <div className="field">
          <label htmlFor="category">Category</label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value as Category)}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="field">
        <label htmlFor="title">Title</label>
        <input
          id="title"
          value={title}
          placeholder="Short summary of the issue"
          aria-invalid={titleInvalid}
          aria-describedby={titleInvalid ? "title-error" : undefined}
          className={titleInvalid ? "is-invalid" : undefined}
          onChange={(e) => setTitle(e.target.value)}
        />
        {validationMessage && (
          <p role="alert" id="title-error" className="field-error">
            {validationMessage}
          </p>
        )}
      </div>

      <div className="field">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          placeholder="What happened, and what did you expect?"
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="form-actions">
        <button type="submit">Submit</button>
      </div>
    </form>
  );
}
