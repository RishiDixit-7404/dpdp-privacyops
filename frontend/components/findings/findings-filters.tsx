"use client";

import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { formatEnumLabel, piiTypeOptions } from "@/lib/format";
import type { FindingFilters, RiskLevel, Scan, SourceType } from "@/lib/types";

interface FindingsFiltersProps {
  filters: FindingFilters;
  scans?: Scan[];
  onChange: (filters: FindingFilters) => void;
}

const riskOptions: RiskLevel[] = ["critical", "high", "medium", "low"];
const sourceOptions: SourceType[] = ["csv", "postgres", "json"];

export function FindingsFilters({ filters, scans = [], onChange }: FindingsFiltersProps) {
  function update(next: FindingFilters) {
    onChange({ ...filters, ...next, offset: 0 });
  }

  return (
    <div className="grid gap-3 rounded-lg border border-border bg-surface p-4 md:grid-cols-5">
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Risk</span>
        <Select
          value={filters.risk_level ?? "all"}
          onChange={(event) =>
            update({ risk_level: event.target.value === "all" ? undefined : (event.target.value as RiskLevel) })
          }
        >
          <option value="all">All risks</option>
          {riskOptions.map((risk) => (
            <option key={risk} value={risk}>
              {formatEnumLabel(risk)}
            </option>
          ))}
        </Select>
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">PII Type</span>
        <Select
          value={filters.pii_type ?? "all"}
          onChange={(event) => update({ pii_type: event.target.value === "all" ? undefined : event.target.value })}
        >
          <option value="all">All PII types</option>
          {piiTypeOptions.map((type) => (
            <option key={type} value={type}>
              {formatEnumLabel(type)}
            </option>
          ))}
        </Select>
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Source Type</span>
        <Select
          value={filters.source_type ?? "all"}
          onChange={(event) =>
            update({ source_type: event.target.value === "all" ? undefined : (event.target.value as SourceType) })
          }
        >
          <option value="all">All sources</option>
          {sourceOptions.map((source) => (
            <option key={source} value={source}>
              {source.toUpperCase()}
            </option>
          ))}
        </Select>
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Scan</span>
        <Select
          value={filters.scan_id ?? "all"}
          onChange={(event) => update({ scan_id: event.target.value === "all" ? undefined : event.target.value })}
        >
          <option value="all">All scans</option>
          {scans.map((scan) => (
            <option key={scan.id} value={scan.id}>
              {scan.source}
            </option>
          ))}
        </Select>
      </label>
      <div className="flex items-end">
        <Button
          className="w-full"
          onClick={() => onChange({ limit: filters.limit ?? 100, offset: 0 })}
          variant="secondary"
        >
          Reset filters
        </Button>
      </div>
    </div>
  );
}

