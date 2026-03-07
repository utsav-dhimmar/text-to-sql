import { zodResolver } from "@hookform/resolvers/zod";
import { RiGithubFill, RiGoogleFill } from "@remixicon/react";
import { useTransition } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button, Input } from "../../components/ui";
import { loginSchema, type LoginFormValues } from "../../schema/user.schema";

export default function LoginPage() {
  const [isPending, startTransition] = useTransition();
  // DAR KE AAGE MOT HAI !!
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginFormValues) => {
    startTransition(async () => {
      console.log("Login data:", data);
      // TODO: REPLACE THIS WITH REAL API
      await new Promise((resolve) => setTimeout(resolve, 2000));
    });
  };

  return (
    <AuthLayout title="Welcome back">
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
            <span className="px-2 bg-white text-neutral-500">Or continue with</span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <Button
            type="button"
            variant="outline"
            icon={<RiGithubFill className="h-5 w-5" />}
            onClick={(e) => console.log("Github login")}
          >
            GitHub
          </Button>
          <Button
            type="button"
            variant="outline"
            icon={<RiGoogleFill className="h-5 w-5" />}
            onClick={(e) => console.log("Google login")}
          >
            Google
          </Button>
        </div>
      </div>

      <p className="mt-8 text-center text-sm text-neutral-600">
        Not a member?{" "}
        <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
