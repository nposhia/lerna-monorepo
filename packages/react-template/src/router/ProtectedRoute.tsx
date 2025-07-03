import type { JSX, ReactNode } from "react";
import { Navigate } from "react-router-dom";

interface ProtectedRouteProps {
	isAdmin: boolean;
	children: ReactNode; // ReactNode is more flexible and covers all valid React children
}

const ProtectedRoute = ({
	isAdmin,
	children,
}: ProtectedRouteProps): JSX.Element => {
	if (!isAdmin) {
		return <Navigate to="/dashboard" />;
	}

	return <>{children}</>;
};

export default ProtectedRoute;
