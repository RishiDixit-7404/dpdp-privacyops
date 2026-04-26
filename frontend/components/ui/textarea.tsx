import type { TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/format";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-[96px] w-full rounded-md border border-border bg-white px-3 py-2 text-sm text-foreground outline-none transition placeholder:text-muted-foreground focus:border-primary focus:ring-2 focus:ring-cyan-100",
        className
      )}
      {...props}
    />
  );
}

