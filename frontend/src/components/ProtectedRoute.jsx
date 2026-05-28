import { Navigate, useLocation } from 'react-router-dom';
import { getStoredUser } from '../api/auth';

export default function ProtectedRoute({ children, roles = [] }) {
  const location = useLocation();
  const user = getStoredUser();
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  if (roles.length && !roles.includes(user.role)) return <Navigate to="/forbidden" replace />;
  return children;
}
