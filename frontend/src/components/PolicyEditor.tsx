// Priority, response and resolution minutes (component-map.md:
// AdminPoliciesPage; E6-S2). Published versions are immutable, so there is
// nothing to disable here — editing always creates a new version.

import type { FormEvent } from "react";

import type { Priority } from "../api/types";

interface PolicyEditorProps {
  priority: Priority;
  priorities: Priority[];
  onPriorityChange: (value: Priority) => void;
  responseMinutes: string;
  onResponseMinutesChange: (value: string) => void;
  resolutionMinutes: string;
  onResolutionMinutesChange: (value: string) => void;
  onSubmit: (event: FormEvent) => void;
}

export function PolicyEditor({
  priority,
  priorities,
  onPriorityChange,
  responseMinutes,
  onResponseMinutesChange,
  resolutionMinutes,
  onResolutionMinutesChange,
  onSubmit,
}: PolicyEditorProps): JSX.Element {
  return (
    <form onSubmit={onSubmit} className="policy-form">
      <div className="field">
        <label htmlFor="policy-priority">Priority</label>
        <select
          id="policy-priority"
          value={priority}
          onChange={(e) => onPriorityChange(e.target.value as Priority)}
        >
          {priorities.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="policy-response">Response minutes</label>
        <input
          id="policy-response"
          value={responseMinutes}
          onChange={(e) => onResponseMinutesChange(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="policy-resolution">Resolution minutes</label>
        <input
          id="policy-resolution"
          value={resolutionMinutes}
          onChange={(e) => onResolutionMinutesChange(e.target.value)}
        />
      </div>

      <div className="form-actions">
        <button type="submit">Save new version</button>
      </div>
    </form>
  );
}
