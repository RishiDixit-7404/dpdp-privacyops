import Link from "next/link";

import { DataRequestStatusBadge } from "@/components/data-requests/data-request-status-badge";
import { DataRequestTypeBadge } from "@/components/data-requests/data-request-type-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatDate } from "@/lib/format";
import type { DataRequest } from "@/lib/types";

export function DataRequestList({
  dataRequests,
  projectId
}: {
  dataRequests: DataRequest[];
  projectId: string;
}) {
  if (dataRequests.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-surface px-5 py-8 text-center text-sm text-muted-foreground">
        No User Data Requests match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface">
      <Table>
        <TableHead>
          <TableRow>
            <TableHeader>Type</TableHeader>
            <TableHeader>Status</TableHeader>
            <TableHeader>Requester email</TableHeader>
            <TableHeader>Identifier</TableHeader>
            <TableHeader>Created</TableHeader>
            <TableHeader>Due date</TableHeader>
            <TableHeader>Assigned to</TableHeader>
            <TableHeader>Open details</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {dataRequests.map((dataRequest) => (
            <TableRow key={dataRequest.id}>
              <TableCell>
                <DataRequestTypeBadge requestType={dataRequest.request_type} />
              </TableCell>
              <TableCell>
                <DataRequestStatusBadge status={dataRequest.status} />
              </TableCell>
              <TableCell>
                <div className="max-w-[220px] truncate font-medium text-foreground" title={dataRequest.requester_email}>
                  {dataRequest.requester_email}
                </div>
              </TableCell>
              <TableCell>{dataRequest.requester_identifier || "Not set"}</TableCell>
              <TableCell>{formatDate(dataRequest.created_at)}</TableCell>
              <TableCell>{dataRequest.due_date ? formatDate(dataRequest.due_date) : "Not set"}</TableCell>
              <TableCell>{dataRequest.assigned_to || "Unassigned"}</TableCell>
              <TableCell>
                <Link
                  className="text-sm font-medium text-primary"
                  href={`/projects/${projectId}/requests/${dataRequest.id}`}
                >
                  Open request
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
