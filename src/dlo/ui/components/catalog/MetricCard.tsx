"use client";

import Link from "next/link";
import { BarChart3, Tag, Code, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Metric } from "@/types/manifest";

interface MetricCardProps {
  metric: Metric;
}

export function MetricCard({ metric }: MetricCardProps) {
  return (
    <Link href={`/metrics/${metric.name}`}>
      <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900">
                <BarChart3 className="h-4 w-4 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold group-hover:text-primary transition-colors">
                  {metric.name}
                </CardTitle>
                <Badge variant="secondary" className="text-xs mt-1">
                  metric
                </Badge>
              </div>
            </div>
            <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {metric.description && (
            <CardDescription className="line-clamp-2">{metric.description}</CardDescription>
          )}

          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Code className="h-3.5 w-3.5" />
            <code className="bg-muted px-1.5 py-0.5 rounded truncate max-w-full">
              {metric.expression}
            </code>
          </div>

          {metric.tags && metric.tags.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Tag className="h-3.5 w-3.5 text-muted-foreground" />
              {metric.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {metric.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{metric.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
