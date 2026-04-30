import { ModelDetailClient } from "./client";

// For static export, we generate a placeholder route.
// The actual dynamic routing is handled by FastAPI server serving index.html
// for unknown routes, allowing client-side navigation.
export async function generateStaticParams(): Promise<{ name: string }[]> {
  // Generate a placeholder - the actual models are determined at runtime
  return [{ name: "_placeholder" }];
}

interface ModelDetailPageProps {
  params: Promise<{ name: string }>;
}

export default function ModelDetailPage({ params }: ModelDetailPageProps) {
  return <ModelDetailClient params={params} />;
}
