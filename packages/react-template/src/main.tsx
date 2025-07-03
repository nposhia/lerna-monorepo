import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@/index.css";
// eslint-disable-next-line import/no-extraneous-dependencies
import { BrowserRouter } from "react-router";

import App from "@/App";

createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<BrowserRouter>
			<App />
		</BrowserRouter>
	</StrictMode>,
);
