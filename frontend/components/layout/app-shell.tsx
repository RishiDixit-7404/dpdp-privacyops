"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { TopNav } from "@/components/layout/top-nav";
import { Button } from "@/components/ui/button";
import { apiErrorMessage, getCurrentUser } from "@/lib/api";
import { clearAccessToken, getAccessToken, getCachedAuthUser, setCachedAuthUser } from "@/lib/auth";
import type { AuthMeResponse } from "@/lib/types";

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [auth, setAuth] = useState<AuthMeResponse | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);
  const isPublicPath = pathname.startsWith("/public/");
  const isAuthPath = pathname === "/login" || pathname === "/register";

  useEffect(() => {
    if (isPublicPath || isAuthPath) {
      setIsCheckingAuth(false);
      return;
    }
    const token = getAccessToken();
    if (!token) {
      setIsCheckingAuth(false);
      router.push("/login");
      return;
    }
    const cached = getCachedAuthUser();
    if (cached) {
      setAuth(cached);
    }
    void getCurrentUser()
      .then((current) => {
        setAuth(current);
        setCachedAuthUser(current);
        setAuthError(null);
      })
      .catch((error) => {
        clearAccessToken();
        setAuth(null);
        setAuthError(apiErrorMessage(error));
        router.push("/login");
      })
      .finally(() => {
        setIsCheckingAuth(false);
      });
  }, [isAuthPath, isPublicPath, router]);

  function handleLogout() {
    clearAccessToken();
    setAuth(null);
    router.push("/login");
  }

  if (isPublicPath) {
    return (
      <div className="min-h-screen bg-background">
        <main>{children}</main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-surface">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <Link href="/" className="min-w-0">
            <div className="text-lg font-semibold text-foreground">DPDP PrivacyOps</div>
            <div className="text-sm text-muted-foreground">Find personal data. See risk. Prove readiness.</div>
          </Link>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            {!isAuthPath ? <TopNav /> : null}
            {!isAuthPath && auth ? (
              <div className="flex flex-wrap items-center gap-2 rounded-md border border-border bg-muted px-3 py-2 text-xs text-muted-foreground">
                <span>{auth.user.email}</span>
                {auth.organizations[0] ? <span>{auth.organizations[0].name}</span> : null}
                <Button className="h-8 px-2 text-xs" onClick={handleLogout} variant="ghost">
                  Log out
                </Button>
              </div>
            ) : null}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {authError ? <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{authError}</div> : null}
        {isCheckingAuth && !isAuthPath ? <div className="text-sm text-muted-foreground">Checking session...</div> : children}
      </main>
    </div>
  );
}
