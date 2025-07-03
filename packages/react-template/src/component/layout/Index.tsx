import type { JSX, ReactNode } from "react";

import Footer from "@/component/layout/Footer";
import Header from "@/component/layout/Header";

interface LayoutProps {
	children: ReactNode;
}

const Layout = ({ children }: LayoutProps): JSX.Element => {
	return (
		<div className="min-h-screen flex flex-col">
			<Header />
			<main className="flex-1 bg-gray-50">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
					{children}
				</div>
			</main>
			<Footer />
		</div>
	);
};

export default Layout;
