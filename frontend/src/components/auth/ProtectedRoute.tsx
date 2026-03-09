import { Navigate, useLocation } from "react-router-dom";
import { useAppSelector } from "../../store";

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
  superAdminOnly?: boolean;
}

export const ProtectedRoute = ({
  children,
  adminOnly,
  superAdminOnly,
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, user } = useAppSelector((state) => state.auth);
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    const redirectPath =
      adminOnly || superAdminOnly ? "/admin/login" : "/login";
    return <Navigate to={redirectPath} state={{ from: location }} replace />;
  }

  if (superAdminOnly && user?.role !== "superadmin") {
    return <Navigate to="/" replace />;
  }

  if (adminOnly && user?.role !== "admin" && user?.role !== "superadmin") {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
