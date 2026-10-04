// Reply textarea and submit button (component-map.md: CustomerTicketPage,
// AgentTicketPage; E3-S4, E6-S1, E6-S3).

import type { FormEvent } from "react";

import { Icon } from "./Icon";

interface ReplyBoxProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent) => void;
}

export function ReplyBox({ value, onChange, onSubmit }: ReplyBoxProps): JSX.Element {
  return (
    <form onSubmit={onSubmit} aria-label="Reply box" className="reply-box">
      <label htmlFor="reply-body">Reply</label>
      <textarea
        id="reply-body"
        value={value}
        placeholder="Type your reply…"
        onChange={(e) => onChange(e.target.value)}
      />
      <div className="form-actions">
        <button type="submit">
          <Icon name="send" size={16} />
          Send reply
        </button>
      </div>
    </form>
  );
}
