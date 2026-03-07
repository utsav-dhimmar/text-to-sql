import { RiLoader4Line } from "@remixicon/react";
import { type ButtonHTMLAttributes, type ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  isLoading?: boolean;
  variant?: "primary" | "secondary" | "outline";
  fullWidth?: boolean;
  icon?: ReactNode;
}

export function Button({
  children,
  isLoading,
  variant = "primary",
  fullWidth = true,
  className = "",
  disabled,
  icon,
  ...props
}: ButtonProps) {
  const variants = {
    primary:
      "text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 border border-transparent shadow-sm",
    secondary:
      "text-blue-700 bg-blue-100 hover:bg-blue-200 focus:ring-blue-500 border border-transparent",
    outline:
      "text-neutral-700 bg-white hover:bg-neutral-50 border border-neutral-300 focus:ring-blue-500 shadow-sm",
  };

  const widthStyle = fullWidth ? "w-full" : "";

  return (
    <button
      className={`${variants[variant]} ${widthStyle} ${className}`}
      disabled={isLoading || disabled}
      {...props}
    >
      {isLoading ? <RiLoader4Line className="animate-spin h-5 w-5" /> : icon}
      {children}
    </button>
  );
}
