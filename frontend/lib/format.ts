import type { PiiType, RiskLevel, ScanType, SourceType } from "@/lib/types";

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

export function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatEnumLabel(value: string): string {
  return value.replace(/_/g, " ");
}

export function riskLabel(value: RiskLevel): string {
  return value.toUpperCase();
}

export function sourceTypeLabel(value: SourceType | ScanType): string {
  return value.toUpperCase();
}

export const piiTypeOptions: PiiType[] = [
  "email",
  "indian_phone",
  "pan",
  "aadhaar",
  "upi_id",
  "date_of_birth",
  "person_name",
  "address",
  "student_or_child_data",
  "health_data",
  "employment_data",
  "financial_data",
  "authentication_secret",
  "free_text_possible_pii"
];

export function describeFinding(piiType: string, fieldName: string): string {
  if (piiType === "aadhaar") {
    return `Aadhaar-like data found in ${fieldName}`;
  }
  if (piiType === "indian_phone") {
    return `Phone numbers detected in ${fieldName}`;
  }
  if (piiType === "free_text_possible_pii") {
    return `Free-text field may contain personal data`;
  }
  return `${formatEnumLabel(piiType)} detected in ${fieldName}`;
}

