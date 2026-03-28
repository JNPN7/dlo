import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Database, Tag, FileText, Key, Columns } from 'lucide-react';
import { Header } from '@/components/layout';
import { ColumnTable } from '@/components/detail';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { useManifest } from '@/context';

export function SourceDetail() {
  const { name } = useParams<{ name: string }>();
  const { getSource, isLoading, error } = useManifest();

  const source = name ? getSource(name) : undefined;

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

  if (error || !source) {
    return (
      <div className="flex flex-col">
        <Header title="Source Not Found" />
        <div className="p-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">
                {error?.message || `Source "${name}" not found`}
              </p>
              <Link to="/sources">
                <Button variant="outline" className="mt-4">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Sources
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
        title={source.name}
        description="Source details"
        actions={
          <Link to="/sources">
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
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900">
                <Database className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-xl">{source.name}</CardTitle>
                <CardDescription className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary">source</Badge>
                  {source.details?.type && (
                    <Badge variant="outline">{source.details.type}</Badge>
                  )}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {source.description && (
              <p className="text-muted-foreground">{source.description}</p>
            )}

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {source.details?.full_name && (
                <div className="space-y-1">
                  <p className="text-sm font-medium flex items-center gap-1">
                    <FileText className="h-4 w-4" /> Full Name
                  </p>
                  <code className="text-xs bg-muted px-2 py-1 rounded block">
                    {source.details.full_name}
                  </code>
                </div>
              )}

              {source.primary_key && source.primary_key.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium flex items-center gap-1">
                    <Key className="h-4 w-4" /> Primary Key
                  </p>
                  <div className="flex gap-1 flex-wrap">
                    {source.primary_key.map((col) => (
                      <Badge key={col} variant="secondary">{col}</Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-1">
                <p className="text-sm font-medium flex items-center gap-1">
                  <Columns className="h-4 w-4" /> Columns
                </p>
                <p className="text-sm text-muted-foreground">{source.columns.length} columns</p>
              </div>
            </div>

            {source.tags && source.tags.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium flex items-center gap-1">
                  <Tag className="h-4 w-4" /> Tags
                </p>
                <div className="flex gap-1 flex-wrap">
                  {source.tags.map((tag) => (
                    <Badge key={tag} variant="outline">{tag}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Columns Tab */}
        <Tabs defaultValue="columns">
          <TabsList>
            <TabsTrigger value="columns">Columns ({source.columns.length})</TabsTrigger>
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
          </TabsList>
          <TabsContent value="columns">
            <Card>
              <CardContent className="pt-6">
                <ColumnTable columns={source.columns} />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="metadata">
            <Card>
              <CardContent className="pt-6">
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                  {JSON.stringify(source, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
