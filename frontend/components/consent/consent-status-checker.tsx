"use client";

import { FormEvent, useState } from "react";

import { ConsentStatusBadge } from "@/components/consent/consent-status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError, apiErrorMessage, getConsentStatus } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { ConsentStatusResponse } from "@/lib/types";

export function ConsentStatusChecker({ projectId }: { projectId: string }) {
  const [externalUserId, setExternalUserId] = useState("");
  const [purpose, setPurpose] = useState("");
  const [status, setStatus] = useState<ConsentStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setStatus(null);
    setIsChecking(true);
    try {
      setStatus(await getConsentStatus(projectId, externalUserId, purpose));
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 404) {
        setError("No consent event found for this user and purpose.");
      } else {
        setError(apiErrorMessage(requestError));
      }
    } finally {
      setIsChecking(false);
    }
  }

  return (
    <div className="grid gap-4">
      <form className="grid gap-3 md:grid-cols-[1fr_1fr_auto]" onSubmit={handleSubmit}>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">External user ID</span>
          <Input onChange={(event) => setExternalUserId(event.target.value)} required value={externalUserId} />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Purpose</span>
          <Input onChange={(event) => setPurpose(event.target.value)} required value={purpose} />
        </label>
        <div className="flex items-end">
          <Button className="w-full" disabled={isChecking} type="submit">
            {isChecking ? "Checking..." : "Check Status"}
          </Button>
        </div>
      </form>
      {error ? <div className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900">{error}</div> : null}
      {status ? (
        <div className="rounded-lg border border-border bg-muted p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-foreground">Current status</span>
            <ConsentStatusBadge status={status.current_status} />
          </div>
          <div className="mt-2 grid gap-1 text-sm text-muted-foreground">
            <div>Notice version: {status.notice_version}</div>
            <div>Source: {status.source || "Not set"}</div>
            <div>Occurred: {formatDate(status.occurred_at)}</div>
            <div className="break-all">Latest event ID: {status.latest_event_id}</div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
