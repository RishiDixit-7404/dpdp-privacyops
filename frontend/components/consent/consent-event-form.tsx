"use client";

import { FormEvent, useState } from "react";

import { ConsentStatusBadge } from "@/components/consent/consent-status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiErrorMessage, createConsentEvent } from "@/lib/api";
import { consentStatusLabel, consentStatusOptions } from "@/lib/format";
import type { ConsentEvent, ConsentEventCreate, ConsentStatus } from "@/lib/types";

interface ConsentEventFormProps {
  apiKey: string;
  projectId: string;
  onCreated: (event: ConsentEvent) => void;
}

function defaultOccurredAt(): string {
  return new Date().toISOString().slice(0, 16);
}

const initialForm = {
  external_user_id: "",
  purpose: "",
  status: "granted" as ConsentStatus,
  notice_version: "",
  source: "",
  occurred_at: defaultOccurredAt(),
  metadata: ""
};

export function ConsentEventForm({ apiKey, projectId, onCreated }: ConsentEventFormProps) {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [created, setCreated] = useState<ConsentEvent | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!apiKey.trim()) {
      setError("Enter a project API key before recording consent events.");
      return;
    }
    setIsSubmitting(true);
    try {
      let metadata: Record<string, unknown> | null = null;
      if (form.metadata.trim()) {
        const parsed = JSON.parse(form.metadata) as unknown;
        if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
          throw new Error("Metadata must be a JSON object.");
        }
        metadata = parsed as Record<string, unknown>;
      }

      const payload: ConsentEventCreate = {
        external_user_id: form.external_user_id,
        purpose: form.purpose,
        status: form.status,
        notice_version: form.notice_version,
        source: form.source || null,
        occurred_at: new Date(form.occurred_at).toISOString(),
        metadata
      };
      const response = await createConsentEvent(projectId, payload, apiKey.trim());
      setCreated(response);
      setForm({ ...initialForm, occurred_at: defaultOccurredAt() });
      onCreated(response);
    } catch (requestError) {
      setError(requestError instanceof SyntaxError ? "Metadata must be valid JSON." : apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="grid gap-4" onSubmit={handleSubmit}>
      <div className="grid gap-3 md:grid-cols-2">
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">External user ID</span>
          <Input
            onChange={(event) => setForm((current) => ({ ...current, external_user_id: event.target.value }))}
            required
            value={form.external_user_id}
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Purpose</span>
          <Input
            onChange={(event) => setForm((current) => ({ ...current, purpose: event.target.value }))}
            placeholder="marketing_whatsapp"
            required
            value={form.purpose}
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Status</span>
          <Select
            value={form.status}
            onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as ConsentStatus }))}
          >
            {consentStatusOptions.map((status) => (
              <option key={status} value={status}>
                {consentStatusLabel(status)}
              </option>
            ))}
          </Select>
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Notice version</span>
          <Input
            onChange={(event) => setForm((current) => ({ ...current, notice_version: event.target.value }))}
            placeholder="v2.1"
            required
            value={form.notice_version}
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Source</span>
          <Input
            onChange={(event) => setForm((current) => ({ ...current, source: event.target.value }))}
            placeholder="web_signup"
            value={form.source}
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Occurred at</span>
          <Input
            onChange={(event) => setForm((current) => ({ ...current, occurred_at: event.target.value }))}
            required
            type="datetime-local"
            value={form.occurred_at}
          />
        </label>
      </div>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Metadata JSON</span>
        <Textarea
          onChange={(event) => setForm((current) => ({ ...current, metadata: event.target.value }))}
          placeholder='{"ip_country":"IN","ui_surface":"signup_checkbox"}'
          value={form.metadata}
        />
      </label>
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <Button disabled={isSubmitting} type="submit">
          {isSubmitting ? "Recording..." : "Record consent event"}
        </Button>
        {created ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Recorded</span>
            <ConsentStatusBadge status={created.status} />
          </div>
        ) : null}
      </div>
    </form>
  );
}
