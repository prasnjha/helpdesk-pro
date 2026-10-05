// Response/request shapes matching specs/design/api-contracts.md

export interface ErrorEnvelope {
  error: { code: string; message: string };
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  role: "customer" | "agent" | "admin";
  username: string;
}

export type Category = "Billing" | "Technical" | "Account";
export type Priority = "Critical" | "High" | "Medium" | "Low";

export interface QueueRef {
  slug: string;
  name: string;
}

export interface CreateTicketRequest {
  title: string;
  description: string;
  category: Category;
  priority: Priority;
}

export interface CreateTicketResponse {
  id: string;
  status: string;
  category: Category;
  priority: Priority;
  queue: QueueRef;
  customer_id: string;
  created_at: string;
}

export interface TicketSummary {
  id: string;
  title: string;
  status: string;
  priority: Priority;
  category: Category;
  updated_at: string;
}

export type Status = "OPEN" | "IN_PROGRESS" | "PENDING_CUSTOMER" | "RESOLVED" | "CLOSED";

export interface TicketReply {
  id: number;
  ticket_id: string;
  author_id: string;
  author_role: string;
  body: string;
  created_at: string;
}

export interface TicketNote {
  id: number;
  ticket_id: string;
  author_id: string;
  body: string;
  created_at: string;
}

export interface TicketHistoryEntry {
  id: number;
  ticket_id: string;
  event: string;
  from_state: string | null;
  to_state: string | null;
  actor_id: string;
  correlation_id: string | null;
  created_at: string;
}

export interface TicketAssignmentEntry {
  id: number;
  ticket_id: string;
  from_user_id: string | null;
  to_user_id: string;
  actor_id: string;
  created_at: string;
}

export interface TicketDetail {
  id: string;
  title: string;
  description: string;
  category: Category;
  priority: Priority;
  status: Status;
  queue: QueueRef;
  customer_id: string;
  assignee_id: string | null;
  escalated: boolean;
  version: number;
  sla_policy_version_id: number;
  created_at: string;
  updated_at: string;
  replies: TicketReply[];
  notes: TicketNote[];
  history: TicketHistoryEntry[];
  assignments: TicketAssignmentEntry[];
}

export type SlaState = "ON_TRACK" | "AT_RISK" | "BREACHED";

export interface SlaTimer {
  target_minutes: number;
  elapsed_minutes: number;
  state: SlaState;
  stopped_at: string | null;
}

export interface SlaSnapshot {
  response: SlaTimer;
  resolution: SlaTimer;
}

export interface QueueTicket {
  id: string;
  title: string;
  priority: Priority;
  status: Status;
  queue: QueueRef;
  assignee_id: string | null;
  escalated: boolean;
  response_state: SlaState;
  resolution_state: SlaState;
}

export interface SlaPolicyVersion {
  id: number;
  priority: Priority;
  version: number;
  response_minutes: number;
  resolution_minutes: number;
  created_by: string;
  published_at: string;
}

export interface DashboardReport {
  open_by_queue: { queue: QueueRef; count: number }[];
  breached_by_priority: { priority: Priority; count: number }[];
  escalations_in_period: number;
}

export interface KbArticleSummary {
  id: number;
  title: string;
  tags: string[];
  updated_at: string;
}

export interface AssignmentResponse {
  id: string;
  status: Status;
  assignee_id: string | null;
}

export interface StatusResponse {
  id: string;
  status: Status;
}

export interface NoteResponse {
  id: number;
  ticket_id: string;
  author_id: string;
  body: string;
  created_at: string;
}

export interface ReplyResponse {
  id: number;
  ticket_id: string;
  author_role: string;
  body: string;
  created_at: string;
  status: Status;
}

export interface KbArticle {
  id: number;
  title: string;
  body: string;
  tags: string[];
  source_ticket_id: string;
  created_by: string;
  updated_at: string;
}
