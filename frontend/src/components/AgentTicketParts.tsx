// Presentational pieces of AgentTicketPage, split out to keep the page
// function short: the CLOSED read-only banner and locked reply area
// (ticket-detail-closed-variant.png — only "Closed tickets cannot be
// changed." and the locked reply box are in scope per component-map.md),
// and the internal-note form. No state or API calls live here.

import type { FormEvent } from "react";

import { Icon } from "./Icon";

export function ClosedTicketBanner(): JSX.Element {
  return (
    <div className="banner banner-info">
      <Icon name="lock" />
      <div className="banner-body">
        <strong>Closed tickets cannot be changed.</strong>
        <p>Replies, notes, claims and status changes are locked for this ticket.</p>
      </div>
    </div>
  );
}

export function LockedReply(): JSX.Element {
  return (
    <div className="locked-reply">
      <Icon name="lock" />
      <span>This ticket is closed. No further replies or notes can be added.</span>
    </div>
  );
}

interface NoteFormProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent) => void;
}

export function NoteForm({ value, onChange, onSubmit }: NoteFormProps): JSX.Element {
  return (
    <form onSubmit={onSubmit} className="note-form">
      <label htmlFor="note-body">Add a note</label>
      <textarea
        id="note-body"
        value={value}
        placeholder="Visible to agents and admins only"
        onChange={(e) => onChange(e.target.value)}
      />
      <div className="form-actions">
        <button type="submit" className="btn-secondary">
          Add note
        </button>
      </div>
    </form>
  );
}
