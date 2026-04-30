import { RelationshipDetailClient } from "./client";

// For static export, we generate a placeholder route.
// The actual dynamic routing is handled by FastAPI server serving index.html
// for unknown routes, allowing client-side navigation.
export async function generateStaticParams(): Promise<{ name: string }[]> {
  // Generate a placeholder - the actual relationships are determined at runtime
  return [{ name: "_placeholder" }];
}

interface RelationshipDetailPageProps {
  params: Promise<{ name: string }>;
}

export default function RelationshipDetailPage({ params }: RelationshipDetailPageProps) {
  return <RelationshipDetailClient params={params} />;
}
