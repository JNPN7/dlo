"use client";

import { GitBranch } from "lucide-react";
import { Header } from "@/components/layout";
import { RelationshipCard } from "@/components/catalog";
import { Skeleton } from "@/components/ui/Skeleton";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { useManifest } from "@/hooks";

function RelationshipCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Skeleton className="h-8 w-8 rounded-lg" />
          <div>
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-16 mt-1" />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-4 w-full" />
        <div className="flex gap-2 items-center">
          <Skeleton className="h-6 w-20" />
          <Skeleton className="h-4 w-4" />
          <Skeleton className="h-6 w-20" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function RelationshipsPage() {
  const { relationships, isLoading, error, refetch } = useManifest();

  if (error) {
    return (
      <div className="flex flex-col">
        <Header title="Relationships" description="Table relationships in your project" />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Relationships</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{error.message}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <Header
        title="Relationships"
        description={`${relationships.length} table relationships in your project`}
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="p-6">
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <RelationshipCardSkeleton key={i} />
            ))}
          </div>
        ) : relationships.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {relationships.map((relationship) => (
              <RelationshipCard key={relationship.name} relationship={relationship} />
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <GitBranch className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No relationships found</h3>
            <p className="text-muted-foreground mt-2">
              Define relationships in your project&apos;s relationships directory.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
