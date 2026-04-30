import { SourceDetailClient } from "./client";

// For static export, we generate a placeholder route.
// The actual dynamic routing is handled by FastAPI server serving index.html
// for unknown routes, allowing client-side navigation.
export async function generateStaticParams(): Promise<{ name: string }[]> {
  // Generate a placeholder - the actual sources are determined at runtime
  return [{ name: "_placeholder" }];
}

interface SourceDetailPageProps {
  params: Promise<{ name: string }>;
}

export default function SourceDetailPage({ params }: SourceDetailPageProps) {
  return <SourceDetailClient params={params} />;
}
