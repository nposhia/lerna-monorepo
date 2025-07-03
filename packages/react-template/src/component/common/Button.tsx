import type { ButtonHTMLAttributes, JSX, ReactNode } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?:
		| "primary"
		| "secondary"
		| "outline"
		| "ghost"
		| "danger"
		| "success";
	size?: "sm" | "md" | "lg" | "xl";
	isLoading?: boolean;
	leftIcon?: ReactNode;
	rightIcon?: ReactNode;
	fullWidth?: boolean;
	disabled?: boolean;
	children: ReactNode;
}

const Button = ({
	variant = "primary",
	size = "md",
	isLoading = false,
	leftIcon,
	rightIcon,
	fullWidth = false,
	disabled = false,
	children,
	className = "",
	...props
}: ButtonProps): JSX.Element => {
	const baseClasses =
		"inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

	const variantClasses = {
		primary:
			"bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 active:bg-blue-800",
		secondary:
			"bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500 active:bg-gray-800",
		outline:
			"border-2 border-blue-600 text-blue-600 bg-transparent hover:bg-blue-50 focus:ring-blue-500 active:bg-blue-100",
		ghost:
			"text-blue-600 bg-transparent hover:bg-blue-50 focus:ring-blue-500 active:bg-blue-100",
		danger:
			"bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 active:bg-red-800",
		success:
			"bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 active:bg-green-800",
	};

	const sizeClasses = {
		sm: "px-3 py-1.5 text-sm",
		md: "px-4 py-2 text-sm",
		lg: "px-6 py-3 text-base",
		xl: "px-8 py-4 text-lg",
	};

	const widthClass = fullWidth ? "w-full" : "";

	const allClasses = [
		baseClasses,
		variantClasses[variant],
		sizeClasses[size],
		widthClass,
		className,
	]
		.filter(Boolean)
		.join(" ");

	return (
		<button className={allClasses} disabled={disabled || isLoading} {...props}>
			{isLoading && (
				<svg
					className="animate-spin -ml-1 mr-2 h-4 w-4"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
				>
					<circle
						className="opacity-25"
						cx="12"
						cy="12"
						r="10"
						stroke="currentColor"
						strokeWidth="4"
					/>
					<path
						className="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					/>
				</svg>
			)}

			{!isLoading && leftIcon != null && (
				<span className="mr-2">{leftIcon}</span>
			)}

			{children}

			{!isLoading && rightIcon != null && (
				<span className="ml-2">{rightIcon}</span>
			)}
		</button>
	);
};

export default Button;
