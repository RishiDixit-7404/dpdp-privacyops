import { Badge } from "@/components/ui/badge";
import { cn, dataRequestStatusLabel } from "@/lib/format";
import type { DataRequestStatus } from "@/lib/types";

const styles: Record<DataRequestStatus, string> = {
  new: "border-blue-300 bg-blue-50 text-blue-900",
  verifying: "border-amber-300 bg-amber-50 text-amber-900",
  in_progress: "border-cyan-400 bg-cyan-50 text-cyan-900",
  completed: "border-emerald-500 bg-emerald-50 text-emerald-900",
  rejected: "border-slate-300 bg-slate-100 text-slate-700"
};

export function DataRequestStatusBadge({ status }: { status: DataRequestStatus }) {
  return <Badge className={cn("whitespace-nowrap", styles[status])}>{dataRequestStatusLabel(status)}</Badge>;
}
