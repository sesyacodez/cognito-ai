import { ProtectedRoute } from "@/components/ProtectedRoute";
import InsightHubClient from "@/components/InsightHub/InsightHubClient";

export default function InsightHubPage() {
  return (
    <ProtectedRoute>
      <InsightHubClient />
    </ProtectedRoute>
  );
}
