import { ConsentStatusBadge } from "@/components/consent/consent-status-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatDate } from "@/lib/format";
import type { ConsentEvent } from "@/lib/types";

export function ConsentEventList({ events }: { events: ConsentEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-surface px-5 py-8 text-center text-sm text-muted-foreground">
        No consent events match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface">
      <Table>
        <TableHead>
          <TableRow>
            <TableHeader>Status</TableHeader>
            <TableHeader>External User ID</TableHeader>
            <TableHeader>Purpose</TableHeader>
            <TableHeader>Notice Version</TableHeader>
            <TableHeader>Source</TableHeader>
            <TableHeader>Occurred At</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {events.map((event) => (
            <TableRow key={event.id}>
              <TableCell>
                <ConsentStatusBadge status={event.status} />
              </TableCell>
              <TableCell>
                <div className="max-w-[220px] truncate font-medium text-foreground" title={event.external_user_id}>
                  {event.external_user_id}
                </div>
              </TableCell>
              <TableCell>{event.purpose}</TableCell>
              <TableCell>{event.notice_version}</TableCell>
              <TableCell>{event.source || "Not set"}</TableCell>
              <TableCell>{formatDate(event.occurred_at)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
