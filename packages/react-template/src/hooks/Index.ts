import { useEffect, useState } from "react";

const useIsMobile = (breakpoint: number = 768): boolean => {
	const [isMobile, setIsMobile] = useState<boolean>(
		typeof window !== "undefined" ? window.innerWidth < breakpoint : false,
	);

	useEffect(() => {
		const handleResize = (): void => {
			setIsMobile(window.innerWidth < breakpoint);
		};

		window.addEventListener("resize", handleResize);

		return () => window.removeEventListener("resize", handleResize);
	}, [breakpoint]);

	return isMobile;
};

export default useIsMobile;
