import { MetricDetailClient } from "./client";

// For static export, we generate a placeholder route.
// The actual dynamic routing is handled by FastAPI server serving index.html
// for unknown routes, allowing client-side navigation.
export async function generateStaticParams(): Promise<{ name: string }[]> {
  // Generate a placeholder - the actual metrics are determined at runtime
  return [{ name: "_placeholder" }];
}

interface MetricDetailPageProps {
  params: Promise<{ name: string }>;
}

export default function MetricDetailPage({ params }: MetricDetailPageProps) {
  return <MetricDetailClient params={params} />;
}
