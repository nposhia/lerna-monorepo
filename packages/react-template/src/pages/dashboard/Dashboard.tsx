import type { JSX } from "react";
import { Outlet } from "react-router-dom";

const DashboardLayout = (): JSX.Element => (
	<>
		<h2>Unprotected and static route.</h2>
		<p>This is acting as parent for nested route.</p>
		<Outlet />
	</>
);

export default DashboardLayout;
