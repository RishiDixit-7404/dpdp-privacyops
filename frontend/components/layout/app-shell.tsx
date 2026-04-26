import type { ReactNode } from "react";
import Link from "next/link";

import { TopNav } from "@/components/layout/top-nav";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-surface">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <Link href="/" className="min-w-0">
            <div className="text-lg font-semibold text-foreground">DPDP PrivacyOps</div>
            <div className="text-sm text-muted-foreground">Find personal data. See risk. Prove readiness.</div>
          </Link>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <TopNav />
            <div className="rounded-md border border-border bg-muted px-3 py-2 text-xs text-muted-foreground">
              MVP local dashboard — auth not enabled yet.
            </div>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}

