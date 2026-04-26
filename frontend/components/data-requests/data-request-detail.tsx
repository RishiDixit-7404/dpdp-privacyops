"use client";

import { FormEvent, useEffect, useState } from "react";

import { DataRequestStatusBadge } from "@/components/data-requests/data-request-status-badge";
import { DataRequestTypeBadge } from "@/components/data-requests/data-request-type-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiErrorMessage, updateDataRequest } from "@/lib/api";
import { dataRequestStatusLabel, dataRequestStatusOptions, formatDate } from "@/lib/format";
import type { DataRequestDetail as DataRequestDetailType, DataRequestStatus } from "@/lib/types";

interface DataRequestDetailProps {
  dataRequest: DataRequestDetailType;
  onUpdated: (dataRequest: DataRequestDetailType) => void;
}

function toDateTimeLocal(value: string | null): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toISOString().slice(0, 16);
}

export function DataRequestDetail({ dataRequest, onUpdated }: DataRequestDetailProps) {
  const [status, setStatus] = useState<DataRequestStatus>(dataRequest.status);
  const [assignedTo, setAssignedTo] = useState(dataRequest.assigned_to ?? "");
  const [dueDate, setDueDate] = useState(toDateTimeLocal(dataRequest.due_date));
  const [requestDetails, setRequestDetails] = useState(dataRequest.request_details ?? "");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setStatus(dataRequest.status);
    setAssignedTo(dataRequest.assigned_to ?? "");
    setDueDate(toDateTimeLocal(dataRequest.due_date));
    setRequestDetails(dataRequest.request_details ?? "");
  }, [dataRequest]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSaving(true);
    try {
      const updated = await updateDataRequest(dataRequest.id, {
        status,
        assigned_to: assignedTo || null,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        request_details: requestDetails || null
      });
      onUpdated(updated);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Request metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 text-sm md:grid-cols-2">
            <div>
              <dt className="font-medium text-muted-foreground">Type</dt>
              <dd className="mt-1">
                <DataRequestTypeBadge requestType={dataRequest.request_type} />
              </dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Status</dt>
              <dd className="mt-1">
                <DataRequestStatusBadge status={dataRequest.status} />
              </dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Requester email</dt>
              <dd className="break-all text-foreground">{dataRequest.requester_email}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Requester name</dt>
              <dd>{dataRequest.requester_name || "Not provided"}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Identifier</dt>
              <dd>{dataRequest.requester_identifier || "Not provided"}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Created</dt>
              <dd>{formatDate(dataRequest.created_at)}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Updated</dt>
              <dd>{formatDate(dataRequest.updated_at)}</dd>
            </div>
            <div>
              <dt className="font-medium text-muted-foreground">Completed</dt>
              <dd>{dataRequest.completed_at ? formatDate(dataRequest.completed_at) : "Not completed"}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Work request</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={handleSubmit}>
            <div className="grid gap-3 md:grid-cols-3">
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Status</span>
                <Select value={status} onChange={(event) => setStatus(event.target.value as DataRequestStatus)}>
                  {dataRequestStatusOptions.map((statusOption) => (
                    <option key={statusOption} value={statusOption}>
                      {dataRequestStatusLabel(statusOption)}
                    </option>
                  ))}
                </Select>
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Assigned to</span>
                <Input onChange={(event) => setAssignedTo(event.target.value)} value={assignedTo} />
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-xs font-medium text-muted-foreground">Due date</span>
                <Input onChange={(event) => setDueDate(event.target.value)} type="datetime-local" value={dueDate} />
              </label>
            </div>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Request details</span>
              <Textarea
                maxLength={5000}
                onChange={(event) => setRequestDetails(event.target.value)}
                value={requestDetails}
              />
            </label>
            {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
            <Button className="w-full md:w-fit" disabled={isSaving} type="submit">
              {isSaving ? "Saving..." : "Save changes"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
