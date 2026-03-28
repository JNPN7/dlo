import { Box } from 'lucide-react';
import { Header } from '@/components/layout';
import { ModelCard } from '@/components/catalog';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useManifest } from '@/context';

function ModelCardSkeleton() {
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

export function Models() {
  const { models, isLoading, error, refetch } = useManifest();

  if (error) {
    return (
      <div className="flex flex-col">
        <Header title="Models" description="Transformation models in your project" />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Models</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {error.message}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <Header
        title="Models"
        description={`${models.length} transformation models in your project`}
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="p-6">
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <ModelCardSkeleton key={i} />
            ))}
          </div>
        ) : models.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {models.map((model) => (
              <ModelCard key={model.name} model={model} />
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <Box className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No models found</h3>
            <p className="text-muted-foreground mt-2">
              Define models in your project's models directory.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
