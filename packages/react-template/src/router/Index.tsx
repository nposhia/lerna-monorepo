import { lazy } from "react";
import type { RouteObject } from "react-router-dom";

const Home = lazy(() => import("@/pages/home/Index"));
const About = lazy(() => import("@/pages/about/Index"));
const NotFound = lazy(() => import("@/pages/404/NotFound"));
const UserProfile = lazy(() => import("@/pages/user/UserProfile"));
const Dashboard = lazy(() => import("@/pages/dashboard/Dashboard"));
const UserDashboard = lazy(() => import("@/pages/user/UserDashboard"));
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const ProtectedRoute = lazy(() => import("./ProtectedRoute"));

export const routesConfig: RouteObject[] = [
	{
		path: "/",
		element: <Home />,
	},
	{
		path: "/about",
		element: <About />,
	},
	{
		path: "/users/:id",
		element: <UserProfile />,
	},
	{
		path: "/dashboard",
		element: <Dashboard />,
		children: [
			{
				path: "user",
				element: <UserDashboard />,
			},
		],
	},
	{
		path: "/admin",
		element: (
			<ProtectedRoute isAdmin={true}>
				<AdminDashboard />
			</ProtectedRoute>
		),
	},
	{
		path: "*",
		element: <NotFound />,
	},
];

export default routesConfig;
