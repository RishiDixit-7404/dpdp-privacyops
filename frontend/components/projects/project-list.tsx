import Link from "next/link";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/format";
import type { Project } from "@/lib/types";

export function ProjectList({ isLoading, projects }: { isLoading: boolean; projects: Project[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Projects</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? <div className="text-sm text-muted-foreground">Loading projects...</div> : null}
        {!isLoading && projects.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border px-5 py-8 text-center text-sm text-muted-foreground">
            No projects yet. Create one to upload scanner findings.
          </div>
        ) : null}
        <div className="grid gap-3">
          {projects.map((project) => (
            <Link
              className="rounded-lg border border-border bg-white p-4 transition hover:border-primary hover:shadow-soft"
              href={`/projects/${project.id}`}
              key={project.id}
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="font-semibold text-foreground">{project.name}</div>
                  <div className="text-sm text-muted-foreground">{project.organization.name}</div>
                  {project.description ? (
                    <div className="mt-2 text-sm text-muted-foreground">{project.description}</div>
                  ) : null}
                </div>
                <div className="text-xs text-muted-foreground">{formatDate(project.created_at)}</div>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

