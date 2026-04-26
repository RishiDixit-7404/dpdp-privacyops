import { MaskedExamples } from "@/components/findings/masked-examples";
import { RiskBadge } from "@/components/findings/risk-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatConfidence, formatEnumLabel } from "@/lib/format";
import type { ReportTopRisk } from "@/lib/types";

export function TopRisksSection({ topRisks }: { topRisks: ReportTopRisk[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Risks</CardTitle>
      </CardHeader>
      <CardContent>
        {topRisks.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center text-sm text-muted-foreground">
            No top risks available.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-border">
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeader>Risk</TableHeader>
                  <TableHeader>PII Type</TableHeader>
                  <TableHeader>Source</TableHeader>
                  <TableHeader>Field</TableHeader>
                  <TableHeader>Confidence</TableHeader>
                  <TableHeader>Masked Examples</TableHeader>
                  <TableHeader>Suggested Action</TableHeader>
                </TableRow>
              </TableHead>
              <TableBody>
                {topRisks.map((risk) => (
                  <TableRow key={`${risk.source_name}-${risk.field_name}-${risk.pii_type}`}>
                    <TableCell>
                      <RiskBadge risk={risk.risk_level} />
                    </TableCell>
                    <TableCell>{formatEnumLabel(risk.pii_type)}</TableCell>
                    <TableCell>
                      <div className="font-medium uppercase text-foreground">{risk.source_type}</div>
                      <div className="max-w-[180px] truncate text-xs text-muted-foreground" title={risk.source_name}>
                        {risk.source_name}
                      </div>
                    </TableCell>
                    <TableCell>{risk.field_name}</TableCell>
                    <TableCell>{formatConfidence(risk.confidence_score)}</TableCell>
                    <TableCell>
                      <MaskedExamples examples={risk.masked_examples} />
                    </TableCell>
                    <TableCell>
                      <div className="max-w-[320px] text-sm text-foreground">{risk.suggested_action}</div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
