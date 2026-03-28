import { Link } from 'react-router-dom';
import { Box, Tag, Columns, Clock, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Model } from '@/types/manifest';

interface ModelCardProps {
  model: Model;
}

export function ModelCard({ model }: ModelCardProps) {
  const typeColors = {
    materialized: 'bg-emerald-100 dark:bg-emerald-900 text-emerald-600 dark:text-emerald-400',
    view: 'bg-amber-100 dark:bg-amber-900 text-amber-600 dark:text-amber-400',
    ephemeral: 'bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400',
  };

  return (
    <Link to={`/models/${model.name}`}>
      <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${typeColors[model.type]}`}>
                <Box className="h-4 w-4" />
              </div>
              <div>
                <CardTitle className="text-base font-semibold group-hover:text-primary transition-colors">
                  {model.name}
                </CardTitle>
                <Badge variant={model.type} className="text-xs mt-1">
                  {model.type}
                </Badge>
              </div>
            </div>
            <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {model.description && (
            <CardDescription className="line-clamp-2">
              {model.description}
            </CardDescription>
          )}

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Columns className="h-3.5 w-3.5" />
              <span>{model.columns.length} columns</span>
            </div>
            {model.schedule && (
              <div className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                <code className="text-xs">{model.schedule}</code>
              </div>
            )}
          </div>

          {model.depends_on?.nodes && model.depends_on.nodes.length > 0 && (
            <div className="text-xs text-muted-foreground">
              Depends on: {model.depends_on.nodes.slice(0, 2).join(', ')}
              {model.depends_on.nodes.length > 2 && ` +${model.depends_on.nodes.length - 2} more`}
            </div>
          )}

          {model.tags && model.tags.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              <Tag className="h-3.5 w-3.5 text-muted-foreground" />
              {model.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {model.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{model.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
