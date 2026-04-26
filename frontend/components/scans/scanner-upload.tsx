"use client";

import { ChangeEvent, useState } from "react";

import { apiErrorMessage, uploadScannerOutput } from "@/lib/api";
import type { ScannerUploadResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScanSummaryCards } from "@/components/scans/scan-summary-cards";

export function ScannerUpload({
  onUploaded,
  projectId
}: {
  onUploaded: (scan: ScannerUploadResponse) => void;
  projectId: string;
}) {
  const [fileName, setFileName] = useState<string | null>(null);
  const [parsedPayload, setParsedPayload] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedScan, setUploadedScan] = useState<ScannerUploadResponse | null>(null);

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    setUploadedScan(null);
    setParsedPayload(null);
    setError(null);
    setFileName(file?.name ?? null);

    if (!file) {
      return;
    }
    if (!file.name.endsWith(".json")) {
      setError("Upload the scanner JSON output file.");
      return;
    }

    try {
      const text = await file.text();
      setParsedPayload(JSON.parse(text) as unknown);
    } catch {
      setError("This file is not valid JSON.");
    }
  }

  async function handleUpload() {
    if (!parsedPayload) {
      setError("Choose a valid scanner JSON file first.");
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const response = await uploadScannerOutput(projectId, parsedPayload);
      setUploadedScan(response);
      setParsedPayload(null);
      onUploaded(response);
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <Card id="scanner-upload">
      <CardHeader>
        <CardTitle>Upload scanner output</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="text-sm text-muted-foreground">
            Upload the JSON file produced by `dpdp-scanner`. The dashboard shows backend-returned metadata and masked
            examples only.
          </div>
          <Input accept=".json,application/json" onChange={handleFileChange} type="file" />
          {fileName ? <div className="text-sm text-muted-foreground">Selected file: {fileName}</div> : null}
          {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div> : null}
          <Button disabled={!parsedPayload || isUploading} onClick={handleUpload}>
            {isUploading ? "Uploading..." : "Upload scanner JSON"}
          </Button>
          {uploadedScan ? (
            <div className="grid gap-3 rounded-lg border border-border bg-muted p-4">
              <div>
                <div className="text-sm font-semibold text-foreground">Upload complete</div>
                <div className="text-sm text-muted-foreground">
                  Backend scan ID: {uploadedScan.id} · Scanner scan ID: {uploadedScan.scanner_scan_id}
                </div>
              </div>
              <ScanSummaryCards summary={uploadedScan.summary} />
            </div>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}

