import { Badge } from "@/components/ui/badge";
import { cn, riskLabel } from "@/lib/format";
import type { RiskLevel } from "@/lib/types";

const styles: Record<RiskLevel, string> = {
  critical: "border-red-700 bg-red-700 text-white",
  high: "border-orange-500 bg-orange-100 text-orange-900",
  medium: "border-amber-400 bg-amber-50 text-amber-900",
  low: "border-slate-300 bg-slate-100 text-slate-700"
};

export function RiskBadge({ risk }: { risk: RiskLevel }) {
  return <Badge className={cn("whitespace-nowrap", styles[risk])}>{riskLabel(risk)}</Badge>;
}

