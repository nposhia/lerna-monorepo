import { type JSX, Suspense } from "react";
import { useRoutes } from "react-router-dom";

import Layout from "@/component/layout/Index";
import { routesConfig } from "@/router/Index";

const App = (): JSX.Element => {
	const routes = useRoutes(routesConfig);

	return (
		<Layout>
			<Suspense fallback={<div>Loading...</div>}>{routes}</Suspense>
		</Layout>
	);
};

export default App;
