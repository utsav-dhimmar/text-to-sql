import { zodResolver } from "@hookform/resolvers/zod";
import { RiGithubFill, RiGoogleFill } from "@remixicon/react";
import { useTransition } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { registerSchema, type RegisterFormValues } from "../../schema/user.schema";

export default function RegisterPage() {
  const [isPending, startTransition] = useTransition();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data: RegisterFormValues) => {
    startTransition(async () => {
      console.log("Register data:", data);
      await new Promise((resolve) => setTimeout(resolve, 2000));
    });
  };

  return (
    <AuthLayout title="Create an account">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Input
          id="name"
          type="text"
          label="Full name"
          placeholder="Your Name"
          {...register("name")}
          error={errors.name?.message}
        />

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
            <span className="px-2 bg-white text-neutral-500">Or sign up with</span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <Button type="button" variant="outline" icon={<RiGithubFill className="h-5 w-5" />}>
            GitHub
          </Button>
          <Button type="button" variant="outline" icon={<RiGoogleFill className="h-5 w-5" />}>
            Google
          </Button>
        </div>
      </div>

      <p className="mt-8 text-center text-sm text-neutral-600">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
}
