"use client";

import Link from "next/link";
import { GitBranch, Tag, ArrowRight, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { Relationship } from "@/types/manifest";

interface RelationshipCardProps {
  relationship: Relationship;
}

export function RelationshipCard({ relationship }: RelationshipCardProps) {
  return (
    <Link href={`/relationships/${relationship.name}`}>
      <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900">
                <GitBranch className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold group-hover:text-primary transition-colors">
                  {relationship.name}
                </CardTitle>
                <Badge variant="secondary" className="text-xs mt-1">
                  relationship
                </Badge>
              </div>
            </div>
            <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {relationship.description && (
            <CardDescription className="line-clamp-2">
              {relationship.description}
            </CardDescription>
          )}

          <div className="flex items-center gap-2 text-sm">
            <Badge variant="outline">{relationship.from}</Badge>
            <ArrowRight className="h-4 w-4 text-muted-foreground" />
            <Badge variant="outline">{relationship.to}</Badge>
          </div>

          <div className="text-xs text-muted-foreground">
            Joins on: {relationship.from_columns.join(", ")} = {relationship.to_columns.join(", ")}
          </div>

          {relationship.tags && relationship.tags.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Tag className="h-3.5 w-3.5 text-muted-foreground" />
              {relationship.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {relationship.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{relationship.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
