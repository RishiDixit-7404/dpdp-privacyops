import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate, formatEnumLabel } from "@/lib/format";
import type { DataInventorySummary, EvidenceScanSummary } from "@/lib/types";

function CountList({ counts }: { counts: Record<string, number> }) {
  const entries = Object.entries(counts);
  if (entries.length === 0) {
    return <div className="text-sm text-muted-foreground">No items recorded.</div>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {entries.map(([key, value]) => (
        <Badge className="bg-muted text-muted-foreground" key={key}>
          {formatEnumLabel(key)}: {value}
        </Badge>
      ))}
    </div>
  );
}

export function DataInventorySection({
  inventory,
  scanSummary
}: {
  inventory: DataInventorySummary;
  scanSummary: EvidenceScanSummary;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Scan & Data Inventory</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-5">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <div className="text-xs font-medium text-muted-foreground">Latest scan</div>
            <div className="mt-1 text-sm text-foreground">{scanSummary.latest_scan_source ?? "No scans uploaded"}</div>
            <div className="text-xs text-muted-foreground">
              {scanSummary.latest_scan_generated_at ? formatDate(scanSummary.latest_scan_generated_at) : "No generated timestamp"}
            </div>
          </div>
          <div>
            <div className="text-xs font-medium text-muted-foreground">Sources scanned</div>
            <div className="mt-1 text-sm text-foreground">
              {inventory.sources_scanned.length > 0 ? inventory.sources_scanned.join(", ") : "None"}
            </div>
          </div>
          <div>
            <div className="text-xs font-medium text-muted-foreground">Scan types</div>
            <div className="mt-1 text-sm text-foreground">
              {inventory.scan_types.length > 0 ? inventory.scan_types.join(", ") : "None"}
            </div>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="grid gap-2">
            <div className="text-sm font-medium text-foreground">PII type counts</div>
            <CountList counts={inventory.counts_by_pii_type} />
          </div>
          <div className="grid gap-2">
            <div className="text-sm font-medium text-foreground">Source type counts</div>
            <CountList counts={inventory.counts_by_source_type} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
