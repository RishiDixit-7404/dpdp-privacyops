import { Badge } from "@/components/ui/badge";
import { dataRequestTypeLabel } from "@/lib/format";
import type { DataRequestType } from "@/lib/types";

export function DataRequestTypeBadge({ requestType }: { requestType: DataRequestType }) {
  return <Badge className="whitespace-nowrap bg-muted text-muted-foreground">{dataRequestTypeLabel(requestType)}</Badge>;
}
