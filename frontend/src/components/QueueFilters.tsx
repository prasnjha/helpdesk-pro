// Queue and priority filters (component-map.md: WorkbenchPage; E6-S1).

import type { Priority, QueueRef } from "../api/types";

interface QueueFiltersProps {
  queue: string;
  queues: QueueRef[];
  onQueueChange: (value: string) => void;
  priority: Priority | "";
  priorities: Priority[];
  onPriorityChange: (value: Priority | "") => void;
}

export function QueueFilters({
  queue,
  queues,
  onQueueChange,
  priority,
  priorities,
  onPriorityChange,
}: QueueFiltersProps): JSX.Element {
  return (
    <div className="filter-fields">
      <div className="field">
        <label htmlFor="queue-select">Queue</label>
        <select id="queue-select" value={queue} onChange={(e) => onQueueChange(e.target.value)}>
          {queues.map((q) => (
            <option key={q.slug} value={q.slug}>
              {q.name}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="priority-filter">Priority</label>
        <select
          id="priority-filter"
          value={priority}
          onChange={(e) => onPriorityChange(e.target.value as Priority | "")}
        >
          <option value="">All</option>
          {priorities.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
