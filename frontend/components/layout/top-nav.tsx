import Link from "next/link";

const items = [
  { href: "/projects", label: "Projects" },
  { href: "/projects#scanner-upload", label: "Scanner Upload" },
  { href: "/projects#findings", label: "Findings" }
];

export function TopNav() {
  return (
    <nav aria-label="Primary navigation" className="flex flex-wrap items-center gap-2">
      {items.map((item) => (
        <Link
          className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition hover:bg-muted hover:text-foreground"
          href={item.href}
          key={item.href}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

