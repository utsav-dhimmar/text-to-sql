import { zodResolver } from "@hookform/resolvers/zod";
import { RiGoogleFill } from "@remixicon/react";
import { useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import {
  registerSchema,
  type RegisterFormValues,
} from "../../schema/user.schema";
import { AuthService } from "../../apis/service/auth.service";

export default function RegisterPage() {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data: RegisterFormValues) => {
    setError(null);
    startTransition(async () => {
      try {
        console.log("Registering user:", data.email);
        await AuthService.register(data);
        // On success, redirect to login
        navigate("/login");
      } catch (err: any) {
        console.error("Registration failed:", err);
        setError(
          err.response?.data?.detail ||
          "Registration failed. Please try again.",
        );
      }
    });
  };

  return (
    <AuthLayout title="Create an account">
      {error && (
        <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit(onSubmit, (e) => console.log(e))}
        className="space-y-6"
      >
        <Input
          id="email"
          type="email"
          label="Email address"
          placeholder="yourname@example.com"
          {...register("email")}
          error={errors.email?.message}
        />

        <Input
          id="password"
          type="password"
          label="Password"
          placeholder="password go here"
          {...register("password")}
          error={errors.password?.message}
        />

        <Button type="submit" isLoading={isPending}>
          Create account
        </Button>
      </form>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-neutral-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-900 text-neutral-500 dark:text-gray-400">
              Or sign up with
            </span>
          </div>
        </div>

        <div className="mt-6 grid gap-3">
          <Button
            type="button"
            variant="outline"
            icon={<RiGoogleFill className="h-5 w-5" />}
            onClick={() => (window.location.href = "/api/auth/google/login")}
          >
            Google
          </Button>
        </div>
      </div>

      <p className="mt-8 text-center text-sm text-neutral-600 dark:text-gray-400">
        Already have an account?{" "}
        <Link
          to="/login"
          className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
        >
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
