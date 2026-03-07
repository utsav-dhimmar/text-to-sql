import { type InputHTMLAttributes, type Ref } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  ref?: Ref<HTMLInputElement>;
}

export const Input = ({ label, id, error, hint, className = "", ref, ...props }: InputProps) => {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium text-neutral-700">
        {label}
      </label>
      <input
        id={id}
        ref={ref}
        className={`appearance-none block w-full px-3 py-2.5 border border-neutral-300 rounded-lg shadow-sm placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm ${error ? "border-red-500 focus:ring-red-500" : ""}${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
      {hint && !error && <p className="mt-1 text-sm text-neutral-500">{hint}</p>}
    </div>
  );
};

Input.displayName = "Input";
