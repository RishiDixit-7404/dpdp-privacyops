"use client";

import { Button } from "@/components/ui/button";

export function PrintReportButton() {
  return (
    <Button className="no-print" onClick={() => window.print()} variant="secondary">
      Print report
    </Button>
  );
}
