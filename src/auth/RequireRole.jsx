import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export const RequireRole = ({ role, children }) => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;
  if (user.role !== role) return <Navigate to="/" />;
  return children;
};
