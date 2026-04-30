"use client";

import { Database } from "lucide-react";
import { Header } from "@/components/layout";
import { SourceCard } from "@/components/catalog";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useManifest } from "@/hooks";

function SourceCardSkeleton() {
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
        <Skeleton className="h-4 w-3/4" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-16" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function SourcesPage() {
  const { sources, isLoading, error, refetch } = useManifest();

  if (error) {
    return (
      <div className="flex flex-col">
        <Header title="Sources" description="Data sources in your project" />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Sources</CardTitle>
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
        title="Sources"
        description={`${sources.length} data sources in your project`}
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="p-6">
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <SourceCardSkeleton key={i} />
            ))}
          </div>
        ) : sources.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {sources.map((source) => (
              <SourceCard key={source.name} source={source} />
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No sources found</h3>
            <p className="text-muted-foreground mt-2">
              Define sources in your project&apos;s sources directory.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
