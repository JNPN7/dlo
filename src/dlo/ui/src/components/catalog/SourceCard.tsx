import { Link } from 'react-router-dom';
import { Database, Tag, Columns, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Source } from '@/types/manifest';

interface ResourceCardProps {
  source: Source;
}

export function SourceCard({ source }: ResourceCardProps) {
  return (
    <Link to={`/sources/${source.name}`}>
      <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900">
                <Database className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold group-hover:text-primary transition-colors">
                  {source.name}
                </CardTitle>
                <Badge variant="source" className="text-xs mt-1">
                  source
                </Badge>
              </div>
            </div>
            <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {source.description && (
            <CardDescription className="line-clamp-2">
              {source.description}
            </CardDescription>
          )}

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Columns className="h-3.5 w-3.5" />
              <span>{source.columns.length} columns</span>
            </div>
            {source.details?.full_name && (
              <code className="text-xs bg-muted px-1.5 py-0.5 rounded truncate max-w-[200px]">
                {source.details.full_name}
              </code>
            )}
          </div>

          {source.tags && source.tags.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Tag className="h-3.5 w-3.5 text-muted-foreground" />
              {source.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {source.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{source.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
