import { PublicPrivacyRequestForm } from "@/components/data-requests/public-privacy-request-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PublicPrivacyRequestPage({ params }: { params: { projectId: string } }) {
  return (
    <div className="mx-auto grid min-h-screen max-w-2xl gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Privacy Request</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Use this form to request access, correction, deletion, consent withdrawal, or grievance support. This creates a
          User Data Request for the project team to review.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Submit request</CardTitle>
        </CardHeader>
        <CardContent>
          <PublicPrivacyRequestForm projectId={params.projectId} />
        </CardContent>
      </Card>
    </div>
  );
}
