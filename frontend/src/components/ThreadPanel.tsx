// Renders the conversation: notes only when the viewer is staff
// (component-map.md: CustomerTicketPage public replies only, AgentTicketPage
// replies and notes; E3-S3, E3-S4, E6-S1). Messages are styled as the
// avatar + bubble rows of ticket-detail-active.png; internal notes get the
// amber "agents only" tint so they never read as public replies.

import type { ReactNode } from "react";

import type { TicketNote, TicketReply } from "../api/types";
import { formatDateTime } from "../utils/format";
import { Icon } from "./Icon";

interface ThreadPanelProps {
  replies: TicketReply[];
  notes: TicketNote[];
  showNotes: boolean;
  noteForm?: ReactNode;
  replyBox?: ReactNode;
}

function initial(value: string): string {
  return value.slice(0, 1).toUpperCase();
}

export function ThreadPanel({
  replies,
  notes,
  showNotes,
  noteForm,
  replyBox,
}: ThreadPanelProps): JSX.Element {
  return (
    <>
      <section aria-label="Replies" className="card thread">
        <div className="card-header">
          <h2 className="card-title">Replies</h2>
          <span className="count-pill">{replies.length}</span>
        </div>
        <ul className="message-list">
          {replies.map((reply) => (
            <li key={reply.id} className={`message message-${reply.author_role}`}>
              <span className="avatar" aria-hidden="true">
                {initial(reply.author_role)}
              </span>
              <div className="message-bubble">
                <div className="message-meta">
                  <strong>{reply.author_role}:</strong>
                  <time dateTime={reply.created_at}>{formatDateTime(reply.created_at)}</time>
                </div>
                <p className="message-text">{reply.body}</p>
              </div>
            </li>
          ))}
        </ul>
        {replyBox}
      </section>

      {showNotes && (
        <section aria-label="Internal notes" className="card thread thread-notes">
          <div className="card-header">
            <h2 className="card-title">
              <Icon name="lock" size={18} />
              Internal notes
            </h2>
            <span className="chip chip-warning">Agents only</span>
          </div>
          <ul className="message-list">
            {notes.map((note) => (
              <li key={note.id} className="message message-note">
                <span className="avatar" aria-hidden="true">
                  {initial(note.author_id)}
                </span>
                <div className="message-bubble">
                  <div className="message-meta">
                    <span className="message-author">{note.author_id}</span>
                    <time dateTime={note.created_at}>{formatDateTime(note.created_at)}</time>
                  </div>
                  <p className="message-text">{note.body}</p>
                </div>
              </li>
            ))}
          </ul>
          {noteForm}
        </section>
      )}
    </>
  );
}
