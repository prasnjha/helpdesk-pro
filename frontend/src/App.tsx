import { Navigate, Route, Routes } from "react-router-dom";

import { AgentTicketPage } from "./pages/AgentTicketPage";
import { AuthGuard } from "./components/AuthGuard";
import { AdminConsolePage } from "./pages/AdminConsolePage";
import { CustomerTicketPage } from "./pages/CustomerTicketPage";
import { KbArticlePage } from "./pages/KbArticlePage";
import { KbListPage } from "./pages/KbListPage";
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
        path="/admin"
        element={
          <AuthGuard allow={["admin"]}>
            <AdminConsolePage />
          </AuthGuard>
        }
      />
      <Route
        path="/kb"
        element={
          <AuthGuard allow={["customer", "agent", "admin"]}>
            <KbListPage />
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
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
