"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { apiErrorMessage, addDataRequestNote } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { DataRequestAuditEvent, DataRequestNote } from "@/lib/types";

interface DataRequestNotesProps {
  requestId: string;
  notes: DataRequestNote[];
  auditEvents: DataRequestAuditEvent[];
  onChanged: () => void;
}

export function DataRequestNotes({ requestId, notes, auditEvents, onChanged }: DataRequestNotesProps) {
  const [note, setNote] = useState("");
  const [createdBy, setCreatedBy] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await addDataRequestNote(requestId, { note, created_by: createdBy || null });
      setNote("");
      setCreatedBy("");
      onChanged();
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Notes</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <form className="grid gap-3" onSubmit={handleSubmit}>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Note</span>
              <Textarea
                maxLength={5000}
                onChange={(event) => setNote(event.target.value)}
                required
                value={note}
              />
            </label>
            <label className="space-y-1 text-sm">
              <span className="text-xs font-medium text-muted-foreground">Created by</span>
              <Input onChange={(event) => setCreatedBy(event.target.value)} value={createdBy} />
            </label>
            {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
            <Button className="w-full md:w-fit" disabled={isSubmitting} type="submit">
              {isSubmitting ? "Adding..." : "Add note"}
            </Button>
          </form>
          <div className="grid gap-3">
            {notes.length === 0 ? (
              <div className="rounded-lg border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground">
                No notes yet.
              </div>
            ) : null}
            {notes.map((item) => (
              <div className="rounded-lg border border-border bg-white p-4" key={item.id}>
                <div className="text-sm text-foreground">{item.note}</div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {item.created_by || "Unassigned"} · {formatDate(item.created_at)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Audit timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            {auditEvents.map((event) => (
              <div className="rounded-lg border border-border bg-white p-4" key={event.id}>
                <div className="text-sm font-medium text-foreground">{event.message}</div>
                <div className="mt-1 text-xs text-muted-foreground">
                  {event.event_type.replace(/_/g, " ")} · {formatDate(event.created_at)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
