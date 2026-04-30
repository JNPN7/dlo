"use client";

import { useState, useEffect, useMemo, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Search as SearchIcon, Database, Box, GitBranch, BarChart3, X } from "lucide-react";
import { Header } from "@/components/layout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useManifest, type SearchResult } from "@/hooks";

const resourceIcons: Record<string, typeof Database> = {
  source: Database,
  model: Box,
  relationship: GitBranch,
  metric: BarChart3,
};

const resourceColors: Record<string, string> = {
  source: "bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400",
  model: "bg-pink-100 dark:bg-pink-900 text-pink-600 dark:text-pink-400",
  relationship: "bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-400",
  metric: "bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400",
};

function SearchResultCard({ result }: { result: SearchResult }) {
  const Icon = resourceIcons[result.resourceType] || Box;
  const colorClass = resourceColors[result.resourceType] || resourceColors.model;

  const href =
    result.resourceType === "source"
      ? `/sources/${result.name}`
      : result.resourceType === "model"
        ? `/models/${result.name}`
        : result.resourceType === "relationship"
          ? `/relationships/${result.name}`
          : `/metrics/${result.name}`;

  return (
    <Link href={href}>
      <Card className="transition-all hover:shadow-md hover:border-primary/50 group">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-lg shrink-0 ${colorClass}`}
            >
              <Icon className="h-5 w-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium text-foreground group-hover:text-primary transition-colors truncate">
                  {result.name}
                </h3>
                <Badge variant="secondary" className="shrink-0">
                  {result.resourceType}
                </Badge>
                {result.modelType && (
                  <Badge variant="outline" className="shrink-0">
                    {result.modelType}
                  </Badge>
                )}
              </div>
              {result.description && (
                <p className="text-sm text-muted-foreground line-clamp-1">{result.description}</p>
              )}
              {result.tags.length > 0 && (
                <div className="flex gap-1 mt-2 flex-wrap">
                  {result.tags.slice(0, 4).map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {result.tags.length > 4 && (
                    <Badge variant="secondary" className="text-xs">
                      +{result.tags.length - 4}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function SearchResultSkeleton() {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <div className="flex-1">
            <Skeleton className="h-5 w-48 mb-2" />
            <Skeleton className="h-4 w-full" />
            <div className="flex gap-1 mt-2">
              <Skeleton className="h-5 w-12" />
              <Skeleton className="h-5 w-12" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function SearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [debouncedQuery, setDebouncedQuery] = useState(query);
  const [resourceType, setResourceType] = useState<string | undefined>(
    searchParams.get("type") || undefined
  );

  const { search, isLoading } = useManifest();

  // Debounce query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Update URL params
  useEffect(() => {
    const params = new URLSearchParams();
    if (debouncedQuery) params.set("q", debouncedQuery);
    if (resourceType) params.set("type", resourceType);
    router.replace(`/search?${params.toString()}`);
  }, [debouncedQuery, resourceType, router]);

  // Search results from context
  const results = useMemo(() => {
    if (!debouncedQuery) return [];
    return search(debouncedQuery, resourceType);
  }, [debouncedQuery, resourceType, search]);

  const handleClear = () => {
    setQuery("");
    setDebouncedQuery("");
  };

  return (
    <div className="flex flex-col">
      <Header title="Search" description="Find resources across your project" />

      <div className="p-6 space-y-6">
        {/* Search Input */}
        <Card>
          <CardContent>
            <div className="relative">
              <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search by name, description, or tags..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10 pr-10"
                autoFocus
              />
              {query && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
                  onClick={handleClear}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <Tabs
          value={resourceType || "all"}
          onValueChange={(v) => setResourceType(v === "all" ? undefined : v)}
        >
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="source">
              <Database className="h-4 w-4 mr-1" />
              Sources
            </TabsTrigger>
            <TabsTrigger value="model">
              <Box className="h-4 w-4 mr-1" />
              Models
            </TabsTrigger>
            <TabsTrigger value="relationship">
              <GitBranch className="h-4 w-4 mr-1" />
              Relationships
            </TabsTrigger>
            <TabsTrigger value="metric">
              <BarChart3 className="h-4 w-4 mr-1" />
              Metrics
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Results */}
        {!debouncedQuery ? (
          <Card className="p-12 text-center">
            <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">Start searching</h3>
            <p className="text-muted-foreground mt-2">
              Enter a query to search across sources, models, relationships, and metrics.
            </p>
          </Card>
        ) : isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <SearchResultSkeleton key={i} />
            ))}
          </div>
        ) : results.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Found {results.length} result{results.length !== 1 ? "s" : ""} for &quot;
              {debouncedQuery}&quot;
            </p>
            {results.map((result) => (
              <SearchResultCard key={`${result.resourceType}-${result.name}`} result={result} />
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No results found</h3>
            <p className="text-muted-foreground mt-2">
              No resources match &quot;{debouncedQuery}&quot;. Try a different search term.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col h-full">
          <Header title="Search" description="Find resources across your project" />
          <div className="p-6">
            <Skeleton className="h-16 w-full" />
          </div>
        </div>
      }
    >
      <SearchContent />
    </Suspense>
  );
}
