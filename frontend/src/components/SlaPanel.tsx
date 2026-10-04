// SLA targets card (ticket-detail-active.png "SLA Targets"). Shows each
// timer's backend state badge plus its integer elapsed/target minutes as
// returned by GET /api/tickets/{id}/sla — no SLA maths happens here; the bar
// width is only a visual ratio of the two integers, capped at 100 %.

import type { SlaSnapshot, SlaTimer } from "../api/types";
import { Icon } from "./Icon";
import { SlaBadge } from "./SlaBadge";

const BAR_CLASS = { ON_TRACK: "bar-ok", AT_RISK: "bar-warning", BREACHED: "bar-critical" } as const;

function barWidth(timer: SlaTimer): string {
  if (timer.target_minutes <= 0) return "100%";
  return `${Math.min(100, Math.round((timer.elapsed_minutes / timer.target_minutes) * 100))}%`;
}

interface SlaRowProps {
  label: string;
  timer: SlaTimer;
  testId: string;
}

function SlaRow({ label, timer, testId }: SlaRowProps): JSX.Element {
  return (
    <div className="sla-row">
      <p className="sla-row-head" data-testid={testId}>
        <span className="sla-row-label">{label}:</span> <SlaBadge state={timer.state} />
      </p>
      <div className="sla-bar" aria-hidden="true">
        <span className={`sla-bar-fill ${BAR_CLASS[timer.state]}`} style={{ width: barWidth(timer) }} />
      </div>
      <p className="sla-row-minutes">
        {timer.elapsed_minutes} of {timer.target_minutes} min elapsed
      </p>
    </div>
  );
}

interface SlaPanelProps {
  sla: SlaSnapshot;
}

export function SlaPanel({ sla }: SlaPanelProps): JSX.Element {
  return (
    <section aria-label="SLA status" className="card sla-panel">
      <div className="card-header">
        <h2 className="card-title">
          <Icon name="timer" />
          SLA targets
        </h2>
      </div>
      <SlaRow label="Response" timer={sla.response} testId="sla-response-state" />
      <SlaRow label="Resolution" timer={sla.resolution} testId="sla-resolution-state" />
    </section>
  );
}
