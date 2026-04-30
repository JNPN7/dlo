"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, BarChart3, Tag, Code } from "lucide-react";
import { Header } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useManifest } from "@/hooks";

interface MetricDetailClientProps {
  params: Promise<{ name: string }>;
}

export function MetricDetailClient({ params }: MetricDetailClientProps) {
  const { name } = use(params);
  const decodedName = decodeURIComponent(name);
  const { getMetric, isLoading, error } = useManifest();

  const metric = getMetric(decodedName);

  if (isLoading) {
    return (
      <div className="flex flex-col">
        <Header title="Loading..." />
        <div className="p-6 space-y-6">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error || !metric) {
    return (
      <div className="flex flex-col">
        <Header title="Metric Not Found" />
        <div className="p-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">
                {error?.message || `Metric "${decodedName}" not found`}
              </p>
              <Link href="/metrics">
                <Button variant="outline" className="mt-4">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Metrics
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <Header
        title={metric.name}
        description="Metric details"
        actions={
          <Link href="/metrics">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
        }
      />

      <div className="p-6 space-y-6">
        {/* Overview Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900">
                <BarChart3 className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <CardTitle className="text-xl">{metric.name}</CardTitle>
                <CardDescription className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary">metric</Badge>
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {metric.description && <p className="text-muted-foreground">{metric.description}</p>}

            {/* Expression */}
            <div className="space-y-2">
              <p className="text-sm font-medium flex items-center gap-1">
                <Code className="h-4 w-4" /> Expression
              </p>
              <pre className="text-sm bg-muted p-4 rounded-lg overflow-auto">
                {metric.expression}
              </pre>
            </div>

            {/* Tags */}
            {metric.tags && metric.tags.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium flex items-center gap-1">
                  <Tag className="h-4 w-4" /> Tags
                </p>
                <div className="flex gap-1 flex-wrap">
                  {metric.tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Metadata Tab */}
        <Tabs defaultValue="metadata">
          <TabsList>
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
          </TabsList>
          <TabsContent value="metadata">
            <Card>
              <CardContent className="pt-6">
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                  {JSON.stringify(metric, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
