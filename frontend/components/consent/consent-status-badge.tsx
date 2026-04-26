import { Badge } from "@/components/ui/badge";
import { cn, consentStatusLabel } from "@/lib/format";
import type { ConsentStatus } from "@/lib/types";

const styles: Record<ConsentStatus, string> = {
  granted: "border-emerald-500 bg-emerald-50 text-emerald-900",
  withdrawn: "border-slate-400 bg-slate-100 text-slate-800"
};

export function ConsentStatusBadge({ status }: { status: ConsentStatus }) {
  return <Badge className={cn("whitespace-nowrap", styles[status])}>{consentStatusLabel(status)}</Badge>;
}
