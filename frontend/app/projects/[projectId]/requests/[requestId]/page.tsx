"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { DataRequestDetail } from "@/components/data-requests/data-request-detail";
import { DataRequestNotes } from "@/components/data-requests/data-request-notes";
import { apiErrorMessage, getDataRequest } from "@/lib/api";
import type { DataRequestDetail as DataRequestDetailType } from "@/lib/types";

export default function DataRequestDetailPage({
  params
}: {
  params: { projectId: string; requestId: string };
}) {
  const [dataRequest, setDataRequest] = useState<DataRequestDetailType | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadRequest = useCallback(async () => {
    setError(null);
    try {
      setDataRequest(await getDataRequest(params.requestId));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }, [params.requestId]);

  useEffect(() => {
    void loadRequest();
  }, [loadRequest]);

  return (
    <div className="grid gap-6">
      <div>
        <Link className="text-sm font-medium text-primary" href={`/projects/${params.projectId}/requests`}>
          Back to requests
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-foreground">User Data Request</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Review the request, update status, add internal notes, and keep an audit timeline.
        </p>
      </div>
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      {!dataRequest && !error ? <div className="text-sm text-muted-foreground">Loading request...</div> : null}
      {dataRequest ? (
        <>
          <DataRequestDetail dataRequest={dataRequest} onUpdated={setDataRequest} />
          <DataRequestNotes
            auditEvents={dataRequest.audit_events}
            notes={dataRequest.notes}
            onChanged={() => void loadRequest()}
            requestId={dataRequest.id}
          />
        </>
      ) : null}
    </div>
  );
}
