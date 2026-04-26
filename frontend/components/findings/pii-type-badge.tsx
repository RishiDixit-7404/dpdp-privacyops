import { Badge } from "@/components/ui/badge";
import { formatEnumLabel } from "@/lib/format";

export function PiiTypeBadge({ piiType }: { piiType: string }) {
  return <Badge className="border-cyan-700 bg-cyan-50 text-cyan-900">{formatEnumLabel(piiType)}</Badge>;
}

