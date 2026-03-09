import { zodResolver } from "@hookform/resolvers/zod";
import { useState, useTransition } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button, Input } from "../../components/ui";
import { loginSchema, type LoginFormValues } from "../../schema/user.schema";
import { AuthService } from "../../apis/service/auth.service";
import { useAppDispatch } from "../../store";
import { setCredentials, logout } from "../../store/slices/authSlice";
import { ShieldAlert, Lock } from "lucide-react";

export default function AdminLoginPage() {
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
        const res = await AuthService.login(data);

        // Check if the user is an admin
        if (res.user.role !== "admin" && res.user.role !== "superadmin") {
          // If not an admin, logout immediately and show error
          await AuthService.logout();
          dispatch(logout());
          setError("Access Denied: You do not have administrative privileges.");
          return;
        }

        // Dispatch to Redux store
        dispatch(
          setCredentials({
            user: res.user,
            token: res.access_token,
          }),
        );

        // Redirect to admin dashboard
        navigate("/admin");
      } catch (err: any) {
        console.error("Admin login failed:", err);
        setError(
          err.response?.data?.detail ||
            "Login failed. Please check your credentials.",
        );
      }
    });
  };

  return (
    <AuthLayout title="Admin Portal">
      <div className="flex flex-col items-center mb-6">
        <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-full text-indigo-600 dark:text-indigo-400 mb-4">
          <ShieldAlert size={32} />
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <Lock size={18} className="shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Input
          id="email"
          type="email"
          label="Admin Email"
          placeholder="admin@example.com"
          {...register("email")}
          error={errors.email?.message}
        />

        <Input
          id="password"
          type="password"
          label="Password"
          placeholder="Password"
          {...register("password")}
          error={errors.password?.message}
        />

        <Button
          type="submit"
          isLoading={isPending}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3"
        >
          Authenticate
        </Button>
      </form>
    </AuthLayout>
  );
}
