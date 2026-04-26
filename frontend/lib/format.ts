import type { ConsentStatus, DataRequestStatus, DataRequestType, PiiType, RiskLevel, ScanType, SourceType } from "@/lib/types";

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

export const dataRequestStatusOptions: DataRequestStatus[] = [
  "new",
  "verifying",
  "in_progress",
  "completed",
  "rejected"
];

export const dataRequestTypeOptions: DataRequestType[] = [
  "access",
  "correction",
  "deletion",
  "consent_withdrawal",
  "grievance"
];

export const consentStatusOptions: ConsentStatus[] = ["granted", "withdrawn"];

export function dataRequestTypeLabel(value: DataRequestType): string {
  const labels: Record<DataRequestType, string> = {
    access: "Access",
    correction: "Correction",
    deletion: "Deletion",
    consent_withdrawal: "Consent withdrawal",
    grievance: "Grievance"
  };
  return labels[value];
}

export function dataRequestStatusLabel(value: DataRequestStatus): string {
  const labels: Record<DataRequestStatus, string> = {
    new: "New",
    verifying: "Verifying",
    in_progress: "In progress",
    completed: "Completed",
    rejected: "Rejected"
  };
  return labels[value];
}

export function consentStatusLabel(value: ConsentStatus): string {
  const labels: Record<ConsentStatus, string> = {
    granted: "Granted",
    withdrawn: "Withdrawn"
  };
  return labels[value];
}

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
