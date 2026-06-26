'use client'

import { useState, useMemo, useCallback, useEffect } from 'react';
import ReactGridLayout, { useContainerWidth, Layout, LayoutItem as RGLLayoutItem } from 'react-grid-layout';
import { ChartContainer } from '@/components/charts';
import { LayoutDashboard, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { Header } from '@/components/layout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { useDashboards, useDashboardCharts } from '@/hooks';
import type { Dashboard, LayoutItem } from '@/types/dashboard';
import type { ChartConfig } from '@/types/chart';

import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

/** Skeleton for dashboard list items while loading */
function DashboardListSkeleton() {
  return (
    <div className="space-y-2 p-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="p-3 rounded-lg border">
          <Skeleton className="h-4 w-3/4 mb-2" />
          <Skeleton className="h-3 w-full" />
        </div>
      ))}
    </div>
  );
}

/** Skeleton for dashboard grid while loading */
function DashboardGridSkeleton() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <Skeleton className="h-8 w-48 mb-4" />
      <div className="grid grid-cols-3 gap-4 w-full max-w-4xl">
        <Skeleton className="h-48 rounded-lg" />
        <Skeleton className="h-48 rounded-lg col-span-2" />
        <Skeleton className="h-48 rounded-lg col-span-2" />
        <Skeleton className="h-48 rounded-lg" />
      </div>
    </div>
  );
}

/** Individual dashboard list item */
function DashboardListItem({
  dashboard,
  isSelected,
  onClick,
  isCollapsed,
}: {
  dashboard: Dashboard;
  isSelected: boolean;
  onClick: () => void;
  isCollapsed: boolean;
}) {
  if (isCollapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onClick}
            className={cn(
              "w-full flex items-center justify-center p-3 rounded-lg border transition-colors",
              isSelected
                ? "bg-primary/10 border-primary"
                : "hover:bg-muted/50 border-transparent hover:border-border"
            )}
          >
            <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
          </button>
        </TooltipTrigger>
        <TooltipContent side="right">
          <p className="font-medium">{dashboard.name}</p>
          {dashboard.description && (
            <p className="text-xs text-muted-foreground">{dashboard.description}</p>
          )}
        </TooltipContent>
      </Tooltip>
    );
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left p-3 rounded-lg border transition-colors",
        isSelected
          ? "bg-primary/10 border-primary"
          : "hover:bg-muted/50 border-transparent hover:border-border"
      )}
    >
      <div className="flex items-center gap-2">
        <LayoutDashboard className="h-4 w-4 text-muted-foreground flex-shrink-0" />
        <span className="font-medium text-sm truncate">{dashboard.name}</span>
      </div>
      {dashboard.description && (
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
          {dashboard.description}
        </p>
      )}
    </button>
  );
}

/** Left panel with searchable dashboard list */
function DashboardList({
  dashboards,
  isLoading,
  selectedDashboardId,
  onSelectDashboard,
  searchQuery,
  onSearchChange,
  isCollapsed,
  onToggleCollapse,
}: {
  dashboards: Dashboard[];
  isLoading: boolean;
  selectedDashboardId: string | null;
  onSelectDashboard: (dashboardId: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}) {
  const filteredDashboards = useMemo(() => {
    if (!searchQuery.trim()) return dashboards;
    const query = searchQuery.toLowerCase();
    return dashboards.filter(
      (dashboard) =>
        dashboard.name.toLowerCase().includes(query) ||
        dashboard.description?.toLowerCase().includes(query)
    );
  }, [dashboards, searchQuery]);

  return (
    <div className={cn(
      "flex flex-col h-full border-r transition-all duration-300 ease-in-out",
      isCollapsed ? "w-16" : "w-80"
    )}>
      {/* Header with toggle */}
      <div className={cn(
        "flex items-center border-b p-4",
        isCollapsed ? "justify-center" : "justify-between"
      )}>
        {!isCollapsed && (
          <span className="font-semibold text-sm">Dashboards</span>
        )}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onToggleCollapse}
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
              <span className="sr-only">
                {isCollapsed ? "Expand panel" : "Collapse panel"}
              </span>
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            {isCollapsed ? "Expand panel" : "Collapse panel"}
          </TooltipContent>
        </Tooltip>
      </div>

      {/* Search input */}
      {!isCollapsed && (
        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search dashboards..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>
      )}

      {/* Collapsed search icon */}
      {isCollapsed && (
        <div className="p-2 border-b">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className="w-full h-10"
                onClick={onToggleCollapse}
              >
                <Search className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Search dashboards</TooltipContent>
          </Tooltip>
        </div>
      )}

      {/* Dashboard list */}
      <ScrollArea className="flex-1">
        {isLoading ? (
          isCollapsed ? (
            <div className="space-y-2 p-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full rounded-lg" />
              ))}
            </div>
          ) : (
            <DashboardListSkeleton />
          )
        ) : filteredDashboards.length > 0 ? (
          <div className={cn("space-y-2", isCollapsed ? "p-2" : "p-4")}>
            {filteredDashboards.map((dashboard) => (
              <DashboardListItem
                key={dashboard.unique_id}
                dashboard={dashboard}
                isSelected={selectedDashboardId === dashboard.unique_id}
                onClick={() => onSelectDashboard(dashboard.unique_id)}
                isCollapsed={isCollapsed}
              />
            ))}
          </div>
        ) : (
          <div className={cn("text-center", isCollapsed ? "p-2" : "p-8")}>
            {isCollapsed ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex justify-center">
                    <LayoutDashboard className="h-6 w-6 text-muted-foreground" />
                  </div>
                </TooltipTrigger>
                <TooltipContent side="right">
                  {searchQuery ? 'No dashboards match your search' : 'No dashboards available'}
                </TooltipContent>
              </Tooltip>
            ) : (
              <>
                <LayoutDashboard className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">
                  {searchQuery ? 'No dashboards match your search' : 'No dashboards available'}
                </p>
              </>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}

/** Dashboard grid using react-grid-layout */
function DashboardGrid({
  dashboard,
  chartConfigs,
  loadingStates,
  isLoading,
}: {
  dashboard: Dashboard;
  chartConfigs: Record<string, ChartConfig>;
  loadingStates: Record<string, boolean>;
  isLoading: boolean;
}) {
  const { width, containerRef, mounted } = useContainerWidth();
  const [layout, setLayout] = useState<RGLLayoutItem[]>([]);

  // Update layout when dashboard changes
  useEffect(() => {
    if (dashboard?.layout) {
      setLayout(dashboard.layout as RGLLayoutItem[]);
    }
  }, [dashboard]);

  const handleLayoutChange = useCallback((newLayout: Layout) => {
    console.log(newLayout)
    setLayout([...newLayout]);
    // Future: Save layout to backend
  }, []);

  // If no layout or charts defined
  if (!dashboard.layout?.length && !Object.keys(dashboard.charts).length) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <LayoutDashboard className="h-16 w-16 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">{dashboard.name}</h3>
        <p className="text-sm text-muted-foreground mt-2">
          This dashboard has no charts configured
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-6">
      <h2 className="text-xl font-semibold mb-4">{dashboard.name}</h2>
      {dashboard.description && (
        <p className="text-sm text-muted-foreground mb-4">{dashboard.description}</p>
      )}
      <div ref={containerRef}>
        {mounted && width > 0 && (
          <ReactGridLayout
            layout={layout}
            width={width}
            gridConfig={dashboard.grid_config}
            onLayoutChange={handleLayoutChange}
          >
            {layout.map((item) => {
              const chartConfig = chartConfigs[item.i];
              const isChartLoading = loadingStates[item.i] ?? false;
              return (
                <div key={item.i} className="grid-item">
                  <ChartContainer
                    chartConfig={chartConfig}
                    chartKey={item.i}
                    isLoading={isChartLoading}
                    showHeader
                    headerVariant="compact"
                    skeletonVariant="card"
                  />
                </div>
              );
            })}
          </ReactGridLayout>
        )}
      </div>
    </div>
  );
}

/** Right panel displaying the selected dashboard */
function DashboardDisplay({
  dashboard,
}: {
  dashboard: Dashboard | null;
}) {
  // Fetch all chart configs for this dashboard in parallel
  const { chartConfigs, isLoading, loadingStates, errors } = useDashboardCharts(
    dashboard?.charts ?? null
  );

  // No dashboard selected - show placeholder
  if (!dashboard) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <LayoutDashboard className="h-16 w-16 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">Select a dashboard</h3>
        <p className="text-sm text-muted-foreground mt-2">
          Choose a dashboard from the list to view its charts
        </p>
      </div>
    );
  }

  // Show loading skeleton while charts are being fetched
  if (isLoading && Object.keys(chartConfigs).length === 0) {
    return <DashboardGridSkeleton />;
  }

  // Error state (show if all charts failed)
  if (errors && errors.length > 0 && Object.keys(chartConfigs).length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Charts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              {errors[0]?.message || "Failed to load chart configurations"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <DashboardGrid
      dashboard={dashboard}
      chartConfigs={chartConfigs}
      loadingStates={loadingStates}
      isLoading={isLoading}
    />
  );
}

/** Hook to manage panel collapse state with responsive behavior */
function usePanelCollapse() {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Auto-collapse on small screens
  useEffect(() => {
    const checkScreenSize = () => {
      if (window.innerWidth < 768) {
        setIsCollapsed(true);
      }
    };

    // Check initial size
    checkScreenSize();

    // Add resize listener
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const toggleCollapse = useCallback(() => {
    setIsCollapsed(prev => !prev);
  }, []);

  return { isCollapsed, setIsCollapsed, toggleCollapse };
}

export default function DashboardPage() {
  const { dashboards, isLoading, error, refetch } = useDashboards();
  const [selectedDashboardId, setSelectedDashboardId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { isCollapsed, toggleCollapse } = usePanelCollapse();

  // Get the selected dashboard object
  const selectedDashboard = useMemo(
    () => dashboards.find((d) => d.unique_id === selectedDashboardId) ?? null,
    [dashboards, selectedDashboardId]
  );

  // Error loading dashboard list
  if (error) {
    return (
      <div className="flex flex-col h-full">
        <Header title="Dashboards" description="Data dashboards" />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Dashboards</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{error.message}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Dashboards"
        description={`${dashboards.length} dashboard${dashboards.length !== 1 ? 's' : ''} available`}
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="flex flex-1 min-h-0">
        {/* Left panel - Dashboard list */}
        <DashboardList
          dashboards={dashboards}
          isLoading={isLoading}
          selectedDashboardId={selectedDashboardId}
          onSelectDashboard={setSelectedDashboardId}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          isCollapsed={isCollapsed}
          onToggleCollapse={toggleCollapse}
        />

        {/* Right panel - Dashboard display */}
        <div className="flex-1 min-w-0">
          <DashboardDisplay
            key={selectedDashboardId}
            dashboard={selectedDashboard}
          />
        </div>
      </div>
    </div>
  );
}
