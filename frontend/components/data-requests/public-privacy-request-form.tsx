"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiErrorMessage, createPublicDataRequest } from "@/lib/api";
import { dataRequestTypeLabel, dataRequestTypeOptions } from "@/lib/format";
import type { DataRequestCreateInput, DataRequestType, PublicDataRequestConfirmation } from "@/lib/types";

const initialForm: DataRequestCreateInput = {
  request_type: "access",
  requester_name: "",
  requester_email: "",
  requester_identifier: "",
  request_details: ""
};

export function PublicPrivacyRequestForm({ projectId }: { projectId: string }) {
  const [form, setForm] = useState<DataRequestCreateInput>(initialForm);
  const [confirmation, setConfirmation] = useState<PublicDataRequestConfirmation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await createPublicDataRequest(projectId, {
        request_type: form.request_type,
        requester_name: form.requester_name || null,
        requester_email: form.requester_email,
        requester_identifier: form.requester_identifier || null,
        request_details: form.request_details || null
      });
      setConfirmation(response);
      setForm(initialForm);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  if (confirmation) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5">
        <div className="text-sm font-semibold text-emerald-950">{confirmation.message}</div>
        <div className="mt-2 text-sm text-emerald-900">Request ID: {confirmation.request_id}</div>
      </div>
    );
  }

  return (
    <form className="grid gap-4" onSubmit={handleSubmit}>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Request type</span>
        <Select
          required
          value={form.request_type}
          onChange={(event) => setForm((current) => ({ ...current, request_type: event.target.value as DataRequestType }))}
        >
          {dataRequestTypeOptions.map((requestType) => (
            <option key={requestType} value={requestType}>
              {dataRequestTypeLabel(requestType)}
            </option>
          ))}
        </Select>
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Your email</span>
        <Input
          autoComplete="email"
          onChange={(event) => setForm((current) => ({ ...current, requester_email: event.target.value }))}
          required
          type="email"
          value={form.requester_email}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Your name</span>
        <Input
          autoComplete="name"
          onChange={(event) => setForm((current) => ({ ...current, requester_name: event.target.value }))}
          value={form.requester_name ?? ""}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Account identifier</span>
        <Input
          onChange={(event) => setForm((current) => ({ ...current, requester_identifier: event.target.value }))}
          placeholder="user_id, customer_id, phone, or employee_id"
          value={form.requester_identifier ?? ""}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Details</span>
        <Textarea
          maxLength={5000}
          onChange={(event) => setForm((current) => ({ ...current, request_details: event.target.value }))}
          value={form.request_details ?? ""}
        />
      </label>
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      <Button disabled={isSubmitting} type="submit">
        {isSubmitting ? "Submitting..." : "Submit Privacy Request"}
      </Button>
    </form>
  );
}
