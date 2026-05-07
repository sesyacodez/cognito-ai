import WorkspaceClient from "@/components/Workspace/WorkspaceClient";

export default function Page({ params }: { params: any }) {
  return <WorkspaceClient lessonId={params?.lessonId ?? ""} />;
}
