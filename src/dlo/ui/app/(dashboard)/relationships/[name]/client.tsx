"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, GitBranch, Tag, ArrowRight } from "lucide-react";
import { Header } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useManifest } from "@/hooks";

interface RelationshipDetailClientProps {
  params: Promise<{ name: string }>;
}

export function RelationshipDetailClient({ params }: RelationshipDetailClientProps) {
  const { name } = use(params);
  const decodedName = decodeURIComponent(name);
  const { getRelationship, isLoading, error } = useManifest();

  const relationship = getRelationship(decodedName);

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

  if (error || !relationship) {
    return (
      <div className="flex flex-col">
        <Header title="Relationship Not Found" />
        <div className="p-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">
                {error?.message || `Relationship "${decodedName}" not found`}
              </p>
              <Link href="/relationships">
                <Button variant="outline" className="mt-4">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Relationships
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
        title={relationship.name}
        description="Relationship details"
        actions={
          <Link href="/relationships">
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
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900">
                <GitBranch className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <CardTitle className="text-xl">{relationship.name}</CardTitle>
                <CardDescription className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary">relationship</Badge>
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {relationship.description && (
              <p className="text-muted-foreground">{relationship.description}</p>
            )}

            {/* Join Visualization */}
            <div className="space-y-3">
              <p className="text-sm font-medium">Join Definition</p>
              <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
                <div className="flex-1">
                  <Link href={`/models/${relationship.from}`} className="hover:underline">
                    <div className="font-medium text-foreground hover:text-primary transition-colors">
                      {relationship.from}
                    </div>
                  </Link>
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {relationship.from_columns.map((col) => (
                      <Badge key={col} variant="outline" className="text-xs">
                        {col}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col items-center gap-1">
                  <ArrowRight className="h-5 w-5 text-primary" />
                  <span className="text-xs text-muted-foreground">=</span>
                </div>

                <div className="flex-1 text-right">
                  <Link href={`/models/${relationship.to}`} className="hover:underline">
                    <div className="font-medium text-foreground hover:text-primary transition-colors">
                      {relationship.to}
                    </div>
                  </Link>
                  <div className="flex gap-1 mt-2 flex-wrap justify-end">
                    {relationship.to_columns.map((col) => (
                      <Badge key={col} variant="outline" className="text-xs">
                        {col}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Join Condition */}
            <div className="space-y-2">
              <p className="text-sm font-medium">Join Condition (SQL)</p>
              <code className="block text-xs bg-muted p-3 rounded-lg">
                {relationship.from}.{relationship.from_columns.join(", ")} = {relationship.to}.
                {relationship.to_columns.join(", ")}
              </code>
            </div>

            {/* Tags */}
            {relationship.tags && relationship.tags.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium flex items-center gap-1">
                  <Tag className="h-4 w-4" /> Tags
                </p>
                <div className="flex gap-1 flex-wrap">
                  {relationship.tags.map((tag) => (
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
                  {JSON.stringify(relationship, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
