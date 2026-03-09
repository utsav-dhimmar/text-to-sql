import { RiLoader4Line } from "@remixicon/react";
import { type ButtonHTMLAttributes, type ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children?: ReactNode;
  isLoading?: boolean;
  variant?: "primary" | "secondary" | "outline";
  fullWidth?: boolean;
  icon?: ReactNode;
  size?: "default" | "icon";
}

export function Button({
  children,
  isLoading,
  variant = "primary",
  fullWidth = true,
  className = "",
  disabled,
  icon,
  size = "default",
  ...props
}: ButtonProps) {
  const variants = {
    primary:
      "text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 border border-transparent shadow-sm dark:bg-blue-700 dark:hover:bg-blue-800",
    secondary:
      "text-blue-700 bg-blue-100 hover:bg-blue-200 focus:ring-blue-500 border border-transparent dark:bg-blue-900 dark:text-blue-200 dark:hover:bg-blue-800",
    outline:
      "text-neutral-700 bg-white hover:bg-neutral-50 border border-neutral-300 focus:ring-blue-500 shadow-sm dark:bg-gray-900 dark:text-gray-300 dark:border-gray-700 dark:hover:bg-gray-800",
  };

  const widthStyle = fullWidth ? "w-full" : "";
  const sizeStyle = size === "icon" ? "p-2 aspect-square" : "py-2.5 px-4";

  return (
    <button
      className={`${variants[variant]} ${widthStyle} ${sizeStyle} ${className}`}
      disabled={isLoading || disabled}
      {...props}
    >
      {isLoading ? <RiLoader4Line className="animate-spin h-5 w-5" /> : icon}
      {children}
    </button>
  );
}
