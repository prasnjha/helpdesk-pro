// Renders the conversation: notes only when the viewer is staff
// (component-map.md: CustomerTicketPage public replies only, AgentTicketPage
// replies and notes; E3-S3, E3-S4, E6-S1).

import type { ReactNode } from "react";

import type { TicketNote, TicketReply } from "../api/types";

interface ThreadPanelProps {
  replies: TicketReply[];
  notes: TicketNote[];
  showNotes: boolean;
  noteForm?: ReactNode;
  replyBox?: ReactNode;
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
      {showNotes && (
        <section aria-label="Internal notes">
          <h2>Internal notes</h2>
          <ul>
            {notes.map((note) => (
              <li key={note.id}>{note.body}</li>
            ))}
          </ul>
          {noteForm}
        </section>
      )}

      <section aria-label="Replies">
        <h2>Replies</h2>
        <ul>
          {replies.map((reply) => (
            <li key={reply.id}>
              <strong>{reply.author_role}:</strong> {reply.body}
            </li>
          ))}
        </ul>
        {replyBox}
      </section>
    </>
  );
}
