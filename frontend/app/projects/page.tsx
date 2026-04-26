"use client";

import { useEffect, useState } from "react";

import { CreateProjectForm } from "@/components/projects/create-project-form";
import { ProjectList } from "@/components/projects/project-list";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiErrorMessage, getProjects } from "@/lib/api";
import type { Project } from "@/lib/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadProjects() {
    setIsLoading(true);
    setError(null);
    try {
      setProjects(await getProjects());
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadProjects();
  }, []);

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Projects</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Create an MVP workspace for scanner uploads and data-map findings.
        </p>
      </div>
      {error ? (
        <Card>
          <CardHeader>
            <CardTitle>Backend connection</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div>
          </CardContent>
        </Card>
      ) : null}
      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <CreateProjectForm
          onCreated={(project) => {
            setProjects((current) => [project, ...current]);
          }}
        />
        <ProjectList isLoading={isLoading} projects={projects} />
      </div>
    </div>
  );
}

