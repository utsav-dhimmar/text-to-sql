import { zodResolver } from "@hookform/resolvers/zod";
import { RiGithubFill, RiGoogleFill } from "@remixicon/react";
import { useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button, Input } from "../../components/ui";
import { loginSchema, type LoginFormValues } from "../../schema/user.schema";
import { AuthService } from "../../apis/service/auth.service";
import { useAppDispatch } from "../../store";
import { setCredentials } from "../../store/slices/authSlice";

export default function LoginPage() {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginFormValues) => {
    setError(null);
    startTransition(async () => {
      try {
        console.log("Logging in:", data.email);
        const res = await AuthService.login(data);
        
        // Dispatch to Redux store
        dispatch(setCredentials({ 
          user: res.user, 
          token: res.access_token 
        }));
        
        // Redirect to dashboard (root path for now)
        navigate("/");
      } catch (err: any) {
        console.error("Login failed:", err);
        setError(err.response?.data?.detail || "Login failed. Please check your credentials.");
      }
    });
  };

  return (
    <AuthLayout title="Welcome back">
      {error && (
        <div className="mb-4 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
          Sign in
        </Button>
      </form>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-neutral-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-900 text-neutral-500 dark:text-gray-400">
              Or continue with
            </span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <Button
            type="button"
            variant="outline"
            icon={<RiGithubFill className="h-5 w-5" />}
            onClick={() => (window.location.href = "/api/auth/google/login")}
            fullWidth={true}
          >
            GitHub
          </Button>
          <Button
            type="button"
            variant="outline"
            icon={<RiGoogleFill className="h-5 w-5" />}
            onClick={() => (window.location.href = "/api/auth/google/login")}
            fullWidth={true}
          >
            Google
          </Button>
        </div>
      </div>

      <p className="mt-8 text-center text-sm text-neutral-600 dark:text-gray-400">
        Not a member?{" "}
        <Link
          to="/register"
          className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400"
        >
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
