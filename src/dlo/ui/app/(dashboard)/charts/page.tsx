'use client'

import { useState, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { BarChart3, Search } from 'lucide-react';
import { Header } from '@/components/layout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { useCharts, useChartConfig } from '@/hooks';
import type { Chart, ChartConfig } from '@/types/chart';

/** Skeleton for chart list items while loading */
function ChartListSkeleton() {
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

/** Skeleton for chart display area while loading */
function ChartDisplaySkeleton() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <Skeleton className="h-8 w-48 mb-4" />
      <Skeleton className="h-[400px] w-full max-w-3xl rounded-lg" />
    </div>
  );
}

/** Individual chart list item */
function ChartListItem({
  chart,
  isSelected,
  onClick,
}: {
  chart: Chart;
  isSelected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded-lg border transition-colors ${isSelected
        ? 'bg-primary/10 border-primary'
        : 'hover:bg-muted/50 border-transparent hover:border-border'
        }`}
    >
      <div className="flex items-center gap-2">
        <BarChart3 className="h-4 w-4 text-muted-foreground flex-shrink-0" />
        <span className="font-medium text-sm truncate">{chart.name}</span>
      </div>
      {chart.description && (
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
          {chart.description}
        </p>
      )}
    </button>
  );
}

/** Left panel with searchable chart list */
function ChartList({
  charts,
  isLoading,
  selectedChartId,
  onSelectChart,
  searchQuery,
  onSearchChange,
}: {
  charts: Chart[];
  isLoading: boolean;
  selectedChartId: string | null;
  onSelectChart: (chartId: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}) {
  const filteredCharts = useMemo(() => {
    if (!searchQuery.trim()) return charts;
    const query = searchQuery.toLowerCase();
    return charts.filter(
      (chart) =>
        chart.name.toLowerCase().includes(query) ||
        chart.description?.toLowerCase().includes(query)
    );
  }, [charts, searchQuery]);

  return (
    <div className="flex flex-col h-full">
      {/* Search input */}
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search charts..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Chart list */}
      <ScrollArea className="flex-1">
        {isLoading ? (
          <ChartListSkeleton />
        ) : filteredCharts.length > 0 ? (
          <div className="space-y-2 p-4">
            {filteredCharts.map((chart) => (
              <ChartListItem
                key={chart.unique_id}
                chart={chart}
                isSelected={selectedChartId === chart.unique_id}
                onClick={() => onSelectChart(chart.unique_id)}
              />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <BarChart3 className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">
              {searchQuery ? 'No charts match your search' : 'No charts available'}
            </p>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}

function ChartRender({ chartConfig }: { chartConfig: ChartConfig }) {

  if (chartConfig.engine == "echarts") return <ReactECharts
    option={chartConfig || {}}
    style={{ height: '100%', width: '100%' }}
    opts={{ renderer: 'canvas' }}
  />

  if (chartConfig.engine == "custom") return <></>
}

/** Right panel displaying the selected chart */
function ChartDisplay({
  chartId,
  chartName,
}: {
  chartId: string | null;
  chartName: string | null;
}) {
  const { chartConfig, isLoading, error } = useChartConfig(chartId);

  // No chart selected - show placeholder
  if (!chartId) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <BarChart3 className="h-16 w-16 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium text-foreground">Select a chart</h3>
        <p className="text-sm text-muted-foreground mt-2">
          Choose a chart from the list to view its visualization
        </p>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return <ChartDisplaySkeleton />;
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Chart</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{error.message}</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  console.log(chartName)

  // Chart loaded successfully
  return (
    <div className="flex flex-col h-full p-6">
      {chartName && (
        <h2 className="text-xl font-semibold mb-4">{chartName}</h2>
      )}
      <div className="flex-1 min-h-0">
        <ReactECharts
          option={chartConfig?.option || {}}
          style={{ height: '100%', width: '100%' }}
          opts={{ renderer: 'canvas' }}
        />
      </div>
    </div>
  );
}

export default function ChartsPage() {
  const { charts, isLoading, error, refetch } = useCharts();
  const [selectedChartId, setSelectedChartId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Get the selected chart's name for display
  const selectedChart = useMemo(
    () => charts.find((c) => c.unique_id === selectedChartId),
    [charts, selectedChartId]
  );

  // Error loading chart list
  if (error) {
    return (
      <div className="flex flex-col h-full">
        <Header title="Charts" description="Data visualizations" />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Charts</CardTitle>
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
        title="Charts"
        description={`${charts.length} chart${charts.length !== 1 ? 's' : ''} available`}
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="flex flex-1 min-h-0">
        {/* Left panel - Chart list */}
        <div className="w-80 border-r flex-shrink-0">
          <ChartList
            charts={charts}
            isLoading={isLoading}
            selectedChartId={selectedChartId}
            onSelectChart={setSelectedChartId}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
          />
        </div>

        {/* Right panel - Chart display */}
        <div className="flex-1 min-w-0">
          <ChartDisplay
            key={selectedChartId}
            chartId={selectedChartId}
            chartName={selectedChart?.name ?? null}
          />
        </div>
      </div>
    </div>
  );
}
