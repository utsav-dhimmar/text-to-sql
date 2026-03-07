import { type ReactNode } from "react";

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-neutral-900 tracking-tight">
          {title}
        </h2>
        <p className="mt-2 text-center text-sm text-neutral-600">{subtitle}</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md ">
        <div className="bg-white py-8 px-4 shadow-xl border border-neutral-100 sm:rounded-2xl sm:px-10">
          {children}
        </div>
      </div>
    </div>
  );
}
