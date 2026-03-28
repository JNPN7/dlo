import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Box, Tag, FileText, Key, Columns, Clock, Code, GitBranch } from 'lucide-react';
import { Header } from '@/components/layout';
import { ColumnTable } from '@/components/detail';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { useManifest } from '@/context';

export function ModelDetail() {
  const { name } = useParams<{ name: string }>();
  const { getModel, isLoading, error } = useManifest();

  const model = name ? getModel(name) : undefined;

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

  if (error || !model) {
    return (
      <div className="flex flex-col">
        <Header title="Model Not Found" />
        <div className="p-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground">
                {error?.message || `Model "${name}" not found`}
              </p>
              <Link to="/models">
                <Button variant="outline" className="mt-4">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Models
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const typeColors: Record<string, string> = {
    materialized: 'bg-emerald-100 dark:bg-emerald-900 text-emerald-600 dark:text-emerald-400',
    view: 'bg-amber-100 dark:bg-amber-900 text-amber-600 dark:text-amber-400',
    ephemeral: 'bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400',
  };

  return (
    <div className="flex flex-col">
      <Header
        title={model.name}
        description="Model details"
        actions={
          <Link to="/models">
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
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${typeColors[model.type] || typeColors.materialized}`}>
                <Box className="h-5 w-5" />
              </div>
              <div>
                <CardTitle className="text-xl">{model.name}</CardTitle>
                <CardDescription className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary">{model.type}</Badge>
                  {model.compiled && (
                    <Badge variant="outline">compiled</Badge>
                  )}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {model.description && (
              <p className="text-muted-foreground">{model.description}</p>
            )}

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {model.details?.full_name && (
                <div className="space-y-1">
                  <p className="text-sm font-medium flex items-center gap-1">
                    <FileText className="h-4 w-4" /> Full Name
                  </p>
                  <code className="text-xs bg-muted px-2 py-1 rounded block">
                    {model.details.full_name}
                  </code>
                </div>
              )}

              {model.schedule && (
                <div className="space-y-1">
                  <p className="text-sm font-medium flex items-center gap-1">
                    <Clock className="h-4 w-4" /> Schedule
                  </p>
                  <code className="text-xs bg-muted px-2 py-1 rounded block">
                    {model.schedule}
                  </code>
                </div>
              )}

              {model.primary_key && model.primary_key.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium flex items-center gap-1">
                    <Key className="h-4 w-4" /> Primary Key
                  </p>
                  <div className="flex gap-1 flex-wrap">
                    {model.primary_key.map((col) => (
                      <Badge key={col} variant="secondary">{col}</Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-1">
                <p className="text-sm font-medium flex items-center gap-1">
                  <Columns className="h-4 w-4" /> Columns
                </p>
                <p className="text-sm text-muted-foreground">{model.columns.length} columns</p>
              </div>
            </div>

            {model.depends_on?.nodes && model.depends_on.nodes.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium flex items-center gap-1">
                  <GitBranch className="h-4 w-4" /> Dependencies
                </p>
                <div className="flex gap-1 flex-wrap">
                  {model.depends_on.nodes.map((dep) => (
                    <Link key={dep} to={`/models/${dep}`}>
                      <Badge variant="outline" className="hover:bg-accent cursor-pointer">
                        {dep}
                      </Badge>
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {model.tags && model.tags.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium flex items-center gap-1">
                  <Tag className="h-4 w-4" /> Tags
                </p>
                <div className="flex gap-1 flex-wrap">
                  {model.tags.map((tag) => (
                    <Badge key={tag} variant="outline">{tag}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="columns">
          <TabsList>
            <TabsTrigger value="columns">Columns ({model.columns.length})</TabsTrigger>
            <TabsTrigger value="code">SQL Code</TabsTrigger>
            <TabsTrigger value="compiled">Compiled SQL</TabsTrigger>
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
          </TabsList>
          <TabsContent value="columns">
            <Card>
              <CardContent className="pt-6">
                <ColumnTable columns={model.columns} />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="code">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Code className="h-4 w-4" />
                  Raw SQL Code
                </CardTitle>
              </CardHeader>
              <CardContent>
                {model.raw_code ? (
                  <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                    {model.raw_code}
                  </pre>
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    No raw SQL code available
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="compiled">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Code className="h-4 w-4" />
                  Compiled SQL Code
                </CardTitle>
              </CardHeader>
              <CardContent>
                {model.compiled_code ? (
                  <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                    {model.compiled_code}
                  </pre>
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    No compiled SQL code available. Run 'dlo compile' to generate.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="metadata">
            <Card>
              <CardContent className="pt-6">
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                  {JSON.stringify(model, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
