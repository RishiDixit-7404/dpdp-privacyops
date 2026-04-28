"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiErrorMessage, loginUser } from "@/lib/api";
import { setAccessToken, setCachedAuthUser } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await loginUser({ email, password });
      setAccessToken(response.access_token);
      setCachedAuthUser({ user: response.user, organizations: response.organizations });
      router.push("/projects");
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto grid max-w-md gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Log in</h1>
        <p className="mt-1 text-sm text-muted-foreground">Use your local DPDP PrivacyOps account.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={handleSubmit}>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Email</span>
              <Input onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
            </label>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Password</span>
              <Input onChange={(event) => setPassword(event.target.value)} required type="password" value={password} />
            </label>
            {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
            <Button disabled={isSubmitting} type="submit">
              {isSubmitting ? "Logging in..." : "Log in"}
            </Button>
          </form>
        </CardContent>
      </Card>
      <div className="text-sm text-muted-foreground">
        Need a local account?{" "}
        <Link className="font-medium text-primary" href="/register">
          Register
        </Link>
      </div>
    </div>
  );
}
