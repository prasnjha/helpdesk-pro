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

interface MessageProps {
  variant: string;
  avatar: string;
  author: ReactNode;
  createdAt: string;
  body: string;
}

function Message({ variant, avatar, author, createdAt, body }: MessageProps): JSX.Element {
  return (
    <li className={`message message-${variant}`}>
      <span className="avatar" aria-hidden="true">
        {avatar.slice(0, 1).toUpperCase()}
      </span>
      <div className="message-bubble">
        <div className="message-meta">
          {author}
          <time dateTime={createdAt}>{formatDateTime(createdAt)}</time>
        </div>
        <p className="message-text">{body}</p>
      </div>
    </li>
  );
}

export function ThreadPanel({ replies, notes, showNotes, noteForm, replyBox }: ThreadPanelProps): JSX.Element {
  return (
    <>
      <section aria-label="Replies" className="card thread">
        <div className="card-header">
          <h2 className="card-title">Replies</h2>
          <span className="count-pill">{replies.length}</span>
        </div>
        <ul className="message-list">
          {replies.map((reply) => (
            <Message
              key={reply.id}
              variant={reply.author_role}
              avatar={reply.author_role}
              author={<strong>{reply.author_role}:</strong>}
              createdAt={reply.created_at}
              body={reply.body}
            />
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
              <Message
                key={note.id}
                variant="note"
                avatar={note.author_id}
                author={<span className="message-author">{note.author_id}</span>}
                createdAt={note.created_at}
                body={note.body}
              />
            ))}
          </ul>
          {noteForm}
        </section>
      )}
    </>
  );
}
