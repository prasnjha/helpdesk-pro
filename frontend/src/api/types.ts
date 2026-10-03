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
