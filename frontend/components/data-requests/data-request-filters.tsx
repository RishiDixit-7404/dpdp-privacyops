"use client";

import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import {
  dataRequestStatusLabel,
  dataRequestStatusOptions,
  dataRequestTypeLabel,
  dataRequestTypeOptions
} from "@/lib/format";
import type { DataRequestFilters, DataRequestStatus, DataRequestType } from "@/lib/types";

interface DataRequestFiltersProps {
  filters: DataRequestFilters;
  onChange: (filters: DataRequestFilters) => void;
}

export function DataRequestFilters({ filters, onChange }: DataRequestFiltersProps) {
  function update(next: DataRequestFilters) {
    onChange({ ...filters, ...next, offset: 0 });
  }

  return (
    <div className="grid gap-3 rounded-lg border border-border bg-surface p-4 md:grid-cols-3">
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Status</span>
        <Select
          value={filters.status ?? "all"}
          onChange={(event) =>
            update({ status: event.target.value === "all" ? undefined : (event.target.value as DataRequestStatus) })
          }
        >
          <option value="all">All statuses</option>
          {dataRequestStatusOptions.map((status) => (
            <option key={status} value={status}>
              {dataRequestStatusLabel(status)}
            </option>
          ))}
        </Select>
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Type</span>
        <Select
          value={filters.request_type ?? "all"}
          onChange={(event) =>
            update({ request_type: event.target.value === "all" ? undefined : (event.target.value as DataRequestType) })
          }
        >
          <option value="all">All request types</option>
          {dataRequestTypeOptions.map((requestType) => (
            <option key={requestType} value={requestType}>
              {dataRequestTypeLabel(requestType)}
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
