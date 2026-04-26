import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate, sourceTypeLabel } from "@/lib/format";
import type { Scan } from "@/lib/types";

export function ScanList({ isLoading, projectId, scans }: { isLoading: boolean; projectId: string; scans: Scan[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Scans</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? <div className="text-sm text-muted-foreground">Loading scans...</div> : null}
        {!isLoading && scans.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center text-sm text-muted-foreground">
            No scans uploaded yet.
          </div>
        ) : null}
        <div className="grid gap-3">
          {scans.map((scan) => (
            <Link
              className="rounded-lg border border-border bg-white p-4 transition hover:border-primary hover:shadow-soft"
              href={`/projects/${projectId}/scans/${scan.id}`}
              key={scan.id}
            >
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="truncate font-semibold text-foreground">{scan.source}</div>
                    <Badge className="bg-muted text-muted-foreground">{sourceTypeLabel(scan.scan_type)}</Badge>
                  </div>
                  <div className="mt-2 text-sm text-muted-foreground">
                    Scanner {scan.scanner_version} · generated {formatDate(scan.generated_at)}
                  </div>
                </div>
                <div className="text-sm font-medium text-primary">Open scan detail</div>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

