import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const cards = [
  {
    title: "Local Scanner",
    body: "Run discovery inside your environment across CSV, Postgres metadata, JSON logs, and prompt exports."
  },
  {
    title: "Data Map",
    body: "Upload scanner output and see where personal data appears by project, source, table, file, and field."
  },
  {
    title: "Risk Inventory",
    body: "Prioritize Aadhaar, PAN, secrets, logs, prompts, and other high-risk fields without exposing raw values."
  }
];

export default function HomePage() {
  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-border bg-surface p-6 shadow-soft">
        <div className="max-w-3xl">
          <div className="text-sm font-medium text-primary">Dashboard v0</div>
          <h1 className="mt-3 text-3xl font-semibold tracking-normal text-foreground">
            Turn local scanner output into a working privacy data map.
          </h1>
          <p className="mt-3 text-base text-muted-foreground">
            Create a project, upload masked scanner JSON, and review the risky places where personal data appears in
            files, metadata, logs, support tickets, and AI prompts.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/projects">
              <Button>Open Projects</Button>
            </Link>
            <Link href="/projects#scanner-upload">
              <Button variant="secondary">Upload Scanner Output</Button>
            </Link>
          </div>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader>
              <CardTitle>{card.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{card.body}</p>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}

