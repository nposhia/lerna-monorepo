import type { JSX } from "react";

const Header = (): JSX.Element => {
	return (
		<header className="bg-white shadow-sm border-b border-gray-200">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="flex justify-between items-center h-16">
					<div className="flex items-center">
						<div className="flex-shrink-0">
							<h1 className="text-xl font-bold text-gray-900">
								React Template
							</h1>
						</div>
					</div>
					<nav className="hidden md:block">
						<div className="ml-10 flex items-baseline space-x-4">
							<a
								href="/"
								className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
							>
								Home
							</a>
							<a
								href="/about"
								className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
							>
								About
							</a>
							<a
								href="/users/1"
								className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
							>
								UserProfile(1)
							</a>
							<a
								href="/dashboard"
								className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
							>
								Dashboard
							</a>
							<a
								href="/dashboard/user"
								className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
							>
								UserDashboard
							</a>
							<a
								href="/admin"
								className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
							>
								Admin
							</a>
						</div>
					</nav>
					<div className="md:hidden">
						<button
							type="button"
							className="text-gray-900 hover:text-gray-700 p-2 rounded-md text-sm font-medium"
						>
							<svg
								className="h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M4 6h16M4 12h16M4 18h16"
								/>
							</svg>
						</button>
					</div>
				</div>
			</div>
		</header>
	);
};

export default Header;
