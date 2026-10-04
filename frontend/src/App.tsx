import { Navigate, Route, Routes } from "react-router-dom";

import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { AdminPoliciesPage } from "./pages/AdminPoliciesPage";
import { AgentTicketPage } from "./pages/AgentTicketPage";
import { AuthGuard } from "./components/AuthGuard";
import { CustomerTicketPage } from "./pages/CustomerTicketPage";
import { KbArticlePage } from "./pages/KbArticlePage";
import { KbEditorPage } from "./pages/KbEditorPage";
import { KbSearchPage } from "./pages/KbSearchPage";
import { LoginPage } from "./pages/LoginPage";
import { MyTicketsPage } from "./pages/MyTicketsPage";
import { NewTicketPage } from "./pages/NewTicketPage";
import { WorkbenchPage } from "./pages/WorkbenchPage";

export function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/tickets"
        element={
          <AuthGuard allow={["customer"]}>
            <MyTicketsPage />
          </AuthGuard>
        }
      />
      <Route
        path="/tickets/new"
        element={
          <AuthGuard allow={["customer"]}>
            <NewTicketPage />
          </AuthGuard>
        }
      />
      <Route
        path="/tickets/:id"
        element={
          <AuthGuard allow={["customer"]}>
            <CustomerTicketPage />
          </AuthGuard>
        }
      />
      <Route
        path="/agent/queues/:queue"
        element={
          <AuthGuard allow={["agent", "admin"]}>
            <WorkbenchPage />
          </AuthGuard>
        }
      />
      <Route
        path="/agent/tickets/:id"
        element={
          <AuthGuard allow={["agent", "admin"]}>
            <AgentTicketPage />
          </AuthGuard>
        }
      />
      <Route
        path="/admin/sla-policies"
        element={
          <AuthGuard allow={["admin"]}>
            <AdminPoliciesPage />
          </AuthGuard>
        }
      />
      <Route
        path="/admin/dashboard"
        element={
          <AuthGuard allow={["admin"]}>
            <AdminDashboardPage />
          </AuthGuard>
        }
      />
      <Route
        path="/kb"
        element={
          <AuthGuard allow={["customer", "agent", "admin"]}>
            <KbSearchPage />
          </AuthGuard>
        }
      />
      <Route
        path="/kb/:id"
        element={
          <AuthGuard allow={["customer", "agent", "admin"]}>
            <KbArticlePage />
          </AuthGuard>
        }
      />
      <Route
        path="/agent/kb/new"
        element={
          <AuthGuard allow={["agent", "admin"]}>
            <KbEditorPage />
          </AuthGuard>
        }
      />
      <Route
        path="/agent/kb/:id/edit"
        element={
          <AuthGuard allow={["agent", "admin"]}>
            <KbEditorPage />
          </AuthGuard>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
