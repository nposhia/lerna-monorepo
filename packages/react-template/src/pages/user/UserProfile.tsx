import type { JSX } from "react";
import { useParams } from "react-router-dom";
const UserProfile = (): JSX.Element => {
	const { id } = useParams();

	return <div>Hey User ID: {id}. This is your dynamic route</div>;
};

export default UserProfile;
