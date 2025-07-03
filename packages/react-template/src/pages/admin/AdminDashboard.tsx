import type { JSX } from "react";

const AdminDashboard = (): JSX.Element => {
	return (
		<div className="admin-dashboard">
			<h2>Admin Dashboard (Protected)</h2>
			<p>
				Welcome to the admin dashboard. Here you can manage users, view reports,
				and configure settings.
			</p>
			{/* Additional admin functionalities can be added here */}
		</div>
	);
};
export default AdminDashboard;
