export function MaskedExamples({ examples }: { examples: string[] }) {
  if (examples.length === 0) {
    return <span className="text-sm text-muted-foreground">No examples</span>;
  }

  return (
    <div className="flex max-w-xs flex-wrap gap-1.5">
      {examples.slice(0, 3).map((example) => (
        <span
          className="max-w-full truncate rounded-md border border-border bg-muted px-2 py-1 text-xs text-muted-foreground"
          key={example}
          title={example}
        >
          {example}
        </span>
      ))}
    </div>
  );
}

