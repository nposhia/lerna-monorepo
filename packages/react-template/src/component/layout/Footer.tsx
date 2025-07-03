import type { JSX } from "react";

const Footer = (): JSX.Element => {
	return (
		<footer className="bg-gray-900 text-white">
			<div className="border-t border-gray-800 mt-8 pt-8 text-center">
				<p className="text-gray-300 text-sm">
					© {new Date().getFullYear()} React Template. All rights reserved.
				</p>
			</div>
		</footer>
	);
};

export default Footer;
