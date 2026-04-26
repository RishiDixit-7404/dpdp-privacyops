"use client";

import { FormEvent, useState } from "react";

import { apiErrorMessage, createProject } from "@/lib/api";
import type { Project } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export function CreateProjectForm({ onCreated }: { onCreated: (project: Project) => void }) {
  const [organizationName, setOrganizationName] = useState("");
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSubmitting(true);

    try {
      const project = await createProject({
        organization_name: organizationName,
        project_name: projectName,
        description: description || null
      });
      setOrganizationName("");
      setProjectName("");
      setDescription("");
      setMessage("Project created.");
      onCreated(project);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create project</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="grid gap-4" onSubmit={handleSubmit}>
          <label className="grid gap-1 text-sm">
            <span className="font-medium">Organization name</span>
            <Input
              required
              value={organizationName}
              onChange={(event) => setOrganizationName(event.target.value)}
              placeholder="Acme"
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium">Project name</span>
            <Input
              required
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              placeholder="Main App"
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium">Description</span>
            <Textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Production SaaS app, support exports, and logs"
            />
          </label>
          {message ? <div className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{message}</div> : null}
          {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
          <Button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating..." : "Create project"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

