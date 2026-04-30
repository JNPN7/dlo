"use client";

import Link from "next/link";
import {
  Database,
  Box,
  GitBranch,
  BarChart3,
  Columns,
  Tag,
  Clock,
  ArrowRight,
} from "lucide-react";
import { Header } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useManifest } from "@/hooks";

function StatCard({
  title,
  value,
  icon: Icon,
  href,
  description,
}: {
  title: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  description?: string;
}) {
  return (
    <Link href={href} className="group">
      <Card className="transition-all hover:shadow-lg hover:border-primary/50">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-foreground">{value}</div>
          {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
          <div className="flex items-center gap-1 mt-2 text-xs text-primary opacity-0 group-hover:opacity-100 transition-opacity">
            View all <ArrowRight className="h-3 w-3" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function StatCardSkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-4" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-3 w-24 mt-2" />
      </CardContent>
    </Card>
  );
}

function ModelTypesCard({ modelTypes }: { modelTypes: Record<string, number> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Model Types</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {Object.entries(modelTypes).map(([type, count]) => (
            <Badge key={type} variant="secondary" className="text-sm">
              {type}: {count}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function TagsCard({ tags }: { tags: string[] }) {
  const displayTags = tags.slice(0, 10);
  const remaining = tags.length - displayTags.length;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <Tag className="h-4 w-4" />
          Tags ({tags.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {displayTags.map((tag) => (
            <Badge key={tag} variant="outline">
              {tag}
            </Badge>
          ))}
          {remaining > 0 && <Badge variant="secondary">+{remaining} more</Badge>}
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { isLoading, error, refetch, stats } = useManifest();

  if (error) {
    return (
      <div className="flex flex-col">
        <Header title="Dashboard" description="Overview of your data lineage" />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Data</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">{error.message}</p>
              <p className="text-sm text-muted-foreground">
                Make sure you have compiled your project by running:
              </p>
              <code className="block mt-2 p-2 bg-muted rounded text-sm">dlo compile</code>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <Header
        title="Dashboard"
        description="Overview of your data lineage"
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="p-6 space-y-6">
        {/* Main Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {isLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : (
            <>
              <StatCard
                title="Sources"
                value={stats.sources}
                icon={Database}
                href="/sources"
                description="Data sources"
              />
              <StatCard
                title="Models"
                value={stats.models}
                icon={Box}
                href="/models"
                description="Transformation models"
              />
              <StatCard
                title="Relationships"
                value={stats.relationships}
                icon={GitBranch}
                href="/relationships"
                description="Table relationships"
              />
              <StatCard
                title="Metrics"
                value={stats.metrics}
                icon={BarChart3}
                href="/metrics"
                description="Business metrics"
              />
            </>
          )}
        </div>

        {/* Secondary Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {isLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : (
            <>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Total Columns
                  </CardTitle>
                  <Columns className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stats.totalColumns}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stats.totalSourceColumns} from sources, {stats.totalModelColumns} from models
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Scheduled Models
                  </CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stats.scheduledModels}</div>
                  <p className="text-xs text-muted-foreground mt-1">Models with cron schedules</p>
                </CardContent>
              </Card>

              {Object.keys(stats.modelTypes).length > 0 && (
                <ModelTypesCard modelTypes={stats.modelTypes} />
              )}
            </>
          )}
        </div>

        {/* Tags */}
        {!isLoading && stats.uniqueTags.length > 0 && <TagsCard tags={stats.uniqueTags} />}

        {/* Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-4">
              <Link
                href="/lineage"
                className="flex items-center gap-2 p-3 rounded-lg border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <Database className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">View Lineage</p>
                  <p className="text-xs text-muted-foreground">Interactive graph</p>
                </div>
              </Link>
              <Link
                href="/search"
                className="flex items-center gap-2 p-3 rounded-lg border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <Box className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Search</p>
                  <p className="text-xs text-muted-foreground">Find resources</p>
                </div>
              </Link>
              <Link
                href="/models"
                className="flex items-center gap-2 p-3 rounded-lg border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <GitBranch className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Browse Models</p>
                  <p className="text-xs text-muted-foreground">View transformations</p>
                </div>
              </Link>
              <Link
                href="/sources"
                className="flex items-center gap-2 p-3 rounded-lg border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <BarChart3 className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Browse Sources</p>
                  <p className="text-xs text-muted-foreground">View data sources</p>
                </div>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
