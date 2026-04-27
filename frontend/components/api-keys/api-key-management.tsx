"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiErrorMessage, createProjectApiKey, getProjectApiKeys, revokeProjectApiKey } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { ApiKey } from "@/lib/types";

interface ApiKeyManagementProps {
  projectId: string;
  onCreated?: (apiKey: string) => void;
}

export function ApiKeyManagement({ projectId, onCreated }: ApiKeyManagementProps) {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [name, setName] = useState("Consent writer");
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadKeys = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    try {
      setKeys(await getProjectApiKeys(projectId));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void loadKeys();
  }, [loadKeys]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setNewApiKey(null);
    setIsSubmitting(true);
    try {
      const created = await createProjectApiKey(projectId, name);
      setNewApiKey(created.api_key);
      onCreated?.(created.api_key);
      setName("Consent writer");
      await loadKeys();
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRevoke(apiKeyId: string) {
    setError(null);
    try {
      await revokeProjectApiKey(projectId, apiKeyId);
      await loadKeys();
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }

  return (
    <div className="grid gap-4">
      <form className="flex flex-col gap-3 md:flex-row" onSubmit={handleCreate}>
        <label className="flex-1 space-y-1 text-sm">
          <span className="text-xs font-medium text-muted-foreground">Key name</span>
          <Input onChange={(event) => setName(event.target.value)} required value={name} />
        </label>
        <div className="flex items-end">
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create API key"}
          </Button>
        </div>
      </form>

      {newApiKey ? (
        <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
          <div className="font-semibold">Copy this key now. It will not be shown again.</div>
          <code className="mt-2 block break-all rounded bg-white px-2 py-2 text-xs text-foreground">{newApiKey}</code>
        </div>
      ) : null}

      {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
      {isLoading ? <div className="text-sm text-muted-foreground">Loading API keys...</div> : null}

      {keys.length === 0 && !isLoading ? (
        <div className="rounded-lg border border-dashed border-border bg-surface px-5 py-6 text-center text-sm text-muted-foreground">
          No API keys have been created for this project.
        </div>
      ) : null}

      {keys.length > 0 ? (
        <div className="overflow-x-auto rounded-lg border border-border bg-surface">
          <Table>
            <TableHead>
              <TableRow>
                <TableHeader>Name</TableHeader>
                <TableHeader>Prefix</TableHeader>
                <TableHeader>Created</TableHeader>
                <TableHeader>Last used</TableHeader>
                <TableHeader>Status</TableHeader>
                <TableHeader>Action</TableHeader>
              </TableRow>
            </TableHead>
            <TableBody>
              {keys.map((apiKey) => (
                <TableRow key={apiKey.id}>
                  <TableCell>{apiKey.name}</TableCell>
                  <TableCell>
                    <code className="text-xs">{apiKey.key_prefix}</code>
                  </TableCell>
                  <TableCell>{formatDate(apiKey.created_at)}</TableCell>
                  <TableCell>{apiKey.last_used_at ? formatDate(apiKey.last_used_at) : "Never"}</TableCell>
                  <TableCell>{apiKey.revoked_at ? "Revoked" : "Active"}</TableCell>
                  <TableCell>
                    <Button
                      disabled={Boolean(apiKey.revoked_at)}
                      onClick={() => void handleRevoke(apiKey.id)}
                      variant="danger"
                    >
                      Revoke
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}
    </div>
  );
}
