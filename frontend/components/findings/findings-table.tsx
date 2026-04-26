"use client";

import { useState } from "react";

import { MaskedExamples } from "@/components/findings/masked-examples";
import { PiiTypeBadge } from "@/components/findings/pii-type-badge";
import { RiskBadge } from "@/components/findings/risk-badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { describeFinding, formatConfidence } from "@/lib/format";
import type { Finding } from "@/lib/types";

export function FindingsTable({ findings }: { findings: Finding[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (findings.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-surface px-5 py-8 text-center text-sm text-muted-foreground">
        No findings match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface">
      <Table>
        <TableHead>
          <TableRow>
            <TableHeader>Risk</TableHeader>
            <TableHeader>PII Type</TableHeader>
            <TableHeader>Source</TableHeader>
            <TableHeader>Field Path / Column</TableHeader>
            <TableHeader>Confidence</TableHeader>
            <TableHeader>Masked Examples</TableHeader>
            <TableHeader>Suggested Action</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {findings.map((finding) => {
            const isExpanded = expanded === finding.id;
            return (
              <TableRow key={finding.id}>
                <TableCell>
                  <RiskBadge risk={finding.risk_level} />
                </TableCell>
                <TableCell>
                  <PiiTypeBadge piiType={finding.pii_type} />
                </TableCell>
                <TableCell>
                  <div className="space-y-1">
                    <div className="text-sm font-medium uppercase text-foreground">{finding.source_type}</div>
                    <div className="max-w-[180px] truncate text-xs text-muted-foreground" title={finding.source_name}>
                      {finding.source_name}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="max-w-[240px] space-y-1">
                    <div className="break-words font-medium text-foreground">{finding.field_name}</div>
                    <div className="text-xs text-muted-foreground">
                      {describeFinding(finding.pii_type, finding.field_name)}
                    </div>
                  </div>
                </TableCell>
                <TableCell>{formatConfidence(finding.confidence_score)}</TableCell>
                <TableCell>
                  <MaskedExamples examples={finding.masked_examples} />
                </TableCell>
                <TableCell>
                  <div className="max-w-[320px] space-y-2">
                    <p className={isExpanded ? "text-sm text-foreground" : "line-clamp-2 text-sm text-foreground"}>
                      {finding.suggested_action}
                    </p>
                    {finding.suggested_action.length > 100 ? (
                      <Button
                        className="h-8 px-2 text-xs"
                        onClick={() => setExpanded(isExpanded ? null : finding.id)}
                        variant="ghost"
                      >
                        {isExpanded ? "Show less" : "Show more"}
                      </Button>
                    ) : null}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

