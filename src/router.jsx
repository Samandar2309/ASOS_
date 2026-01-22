import { createBrowserRouter } from "react-router-dom";
import Login from "./pages/Login";
import CenterDashboard from "./pages/admin/CenterDashboard";
import TeacherDashboard from "./pages/teacher/TeacherDashboard";
import StudentDashboard from "./pages/student/StudentDashboard";
import { RequireRole } from "./auth/RequireRole";

export const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  {
    path: "/admin",
    element: (
      <RequireRole role="admin">
        <CenterDashboard />
      </RequireRole>
    ),
  },
  {
    path: "/teacher",
    element: (
      <RequireRole role="teacher">
        <TeacherDashboard />
      </RequireRole>
    ),
  },
  {
    path: "/student",
    element: (
      <RequireRole role="student">
        <StudentDashboard />
      </RequireRole>
    ),
  },
]);
