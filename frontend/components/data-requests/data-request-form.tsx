"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiErrorMessage, createDataRequest } from "@/lib/api";
import { dataRequestTypeLabel, dataRequestTypeOptions } from "@/lib/format";
import type { DataRequest, DataRequestCreateInput, DataRequestType } from "@/lib/types";

interface DataRequestFormProps {
  projectId: string;
  onCreated: (dataRequest: DataRequest) => void;
}

const initialForm: DataRequestCreateInput = {
  request_type: "access",
  requester_name: "",
  requester_email: "",
  requester_identifier: "",
  request_details: ""
};

export function DataRequestForm({ projectId, onCreated }: DataRequestFormProps) {
  const [form, setForm] = useState<DataRequestCreateInput>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const created = await createDataRequest(projectId, {
        request_type: form.request_type,
        requester_name: form.requester_name || null,
        requester_email: form.requester_email,
        requester_identifier: form.requester_identifier || null,
        request_details: form.request_details || null
      });
      setForm(initialForm);
      onCreated(created);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="grid gap-4" onSubmit={handleSubmit}>
      <div className="grid gap-3 md:grid-cols-2">
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Request type</span>
          <Select
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
          <span className="text-xs font-medium text-muted-foreground">Requester email</span>
          <Input
            autoComplete="email"
            onChange={(event) => setForm((current) => ({ ...current, requester_email: event.target.value }))}
            required
            type="email"
            value={form.requester_email}
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Requester name</span>
          <Input
            autoComplete="name"
            onChange={(event) => setForm((current) => ({ ...current, requester_name: event.target.value }))}
            value={form.requester_name ?? ""}
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Identifier</span>
          <Input
            onChange={(event) => setForm((current) => ({ ...current, requester_identifier: event.target.value }))}
            placeholder="user_id, customer_id, phone, employee_id"
            value={form.requester_identifier ?? ""}
          />
        </label>
      </div>
      <label className="space-y-1 text-sm">
        <span className="text-xs font-medium text-muted-foreground">Request details</span>
        <Textarea
          maxLength={5000}
          onChange={(event) => setForm((current) => ({ ...current, request_details: event.target.value }))}
          placeholder="What is the user asking for?"
          value={form.request_details ?? ""}
        />
      </label>
      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      <Button className="w-full md:w-fit" disabled={isSubmitting} type="submit">
        {isSubmitting ? "Creating..." : "Create User Data Request"}
      </Button>
    </form>
  );
}
