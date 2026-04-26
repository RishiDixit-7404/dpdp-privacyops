import type { SelectHTMLAttributes } from "react";

import { cn } from "@/lib/format";

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        "h-10 w-full rounded-md border border-border bg-white px-3 text-sm text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-cyan-100",
        className
      )}
      {...props}
    />
  );
}

