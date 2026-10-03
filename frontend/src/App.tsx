import { Navigate, Route, Routes } from "react-router-dom";

import { AuthGuard } from "./components/AuthGuard";
import { LoginPage } from "./pages/LoginPage";
import { MyTicketsPage } from "./pages/MyTicketsPage";
import { NewTicketPage } from "./pages/NewTicketPage";

export function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/tickets"
        element={
          <AuthGuard>
            <MyTicketsPage />
          </AuthGuard>
        }
      />
      <Route
        path="/tickets/new"
        element={
          <AuthGuard>
            <NewTicketPage />
          </AuthGuard>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
