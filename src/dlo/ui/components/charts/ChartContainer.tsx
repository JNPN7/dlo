import { ReactNode } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { ChartConfig } from '@/types/chart';
import { EChartsRenderer } from './EChartsRenderer';
import { ChartSkeleton, ChartSkeletonVariant } from './ChartSkeleton';

export interface ChartContainerProps {
  /** Chart configuration from API */
  chartConfig?: ChartConfig;
  /** Whether the chart is currently loading */
  isLoading: boolean;
  /** Error object if chart loading failed */
  error?: Error | null;
  /** Chart key/identifier for "not found" messages */
  chartKey?: string;
  /** Display title for the chart */
  title?: string;
  /** Whether to show a header bar */
  showHeader?: boolean;
  /** 
   * Header style variant:
   * - 'compact': Small header with muted background (for grid items)
   * - 'large': Larger title text (for standalone display)
   */
  headerVariant?: 'compact' | 'large';
  /** 
   * Skeleton variant to use during loading:
   * - 'card': With header placeholder
   * - 'full': Centered full-height
   * - 'minimal': Simple skeleton
   */
  skeletonVariant?: ChartSkeletonVariant;
  /** Custom empty state placeholder (when no chartConfig and no chartKey) */
  emptyState?: ReactNode;
  /** Additional CSS class names */
  className?: string;
}

/**
 * Shared chart container component that handles loading, error, empty, and success states.
 * Provides consistent chart rendering across different contexts (grid items, standalone display, etc.)
 */
export function ChartContainer({
  chartConfig,
  isLoading,
  error,
  chartKey,
  title,
  showHeader = false,
  headerVariant = 'compact',
  skeletonVariant = 'card',
  emptyState,
  className,
}: ChartContainerProps) {
  // Loading state
  if (isLoading) {
    return <ChartSkeleton variant={skeletonVariant} />;
  }

  // Error state
  if (error) {
    return (
      <div className={cn("flex items-center justify-center h-full p-8", className)}>
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

  // No chart config - show "not found" or custom empty state
  if (!chartConfig) {
    if (emptyState) {
      return <>{emptyState}</>;
    }

    return (
      <div className={cn(
        "h-full w-full flex items-center justify-center bg-muted rounded-lg border",
        className
      )}>
        <span className="text-sm text-muted-foreground">
          {chartKey ? `Chart not found: ${chartKey}` : 'No chart available'}
        </span>
      </div>
    );
  }

  // Chart loaded successfully - render based on engine type
  const displayTitle = title || chartKey;

  // Compact variant (for grid items)
  if (headerVariant === 'compact' && showHeader) {
    return (
      <div className={cn(
        "h-full w-full flex flex-col bg-card rounded-lg border shadow-sm overflow-hidden",
        className
      )}>
        <div className="px-3 py-2 border-b bg-muted/30 flex-shrink-0">
          <h3 className="text-sm font-medium truncate" title={displayTitle}>
            {displayTitle}
          </h3>
        </div>
        <div className="flex-1 min-h-0 p-2">
          {renderChartContent(chartConfig, chartKey)}
        </div>
      </div>
    );
  }

  // Large variant (for standalone display)
  if (headerVariant === 'large' && showHeader && displayTitle) {
    return (
      <div className={cn("flex flex-col h-full p-6", className)}>
        <h2 className="text-xl font-semibold mb-4">{displayTitle}</h2>
        <div className="flex-1 min-h-0">
          {renderChartContent(chartConfig, chartKey)}
        </div>
      </div>
    );
  }

  // No header - just render the chart content
  return (
    <div className={cn("h-full w-full", className)}>
      {renderChartContent(chartConfig, chartKey)}
    </div>
  );
}

/**
 * Helper function to render chart content based on engine type
 */
function renderChartContent(chartConfig: ChartConfig, chartKey?: string) {
  if (chartConfig.engine === 'echarts') {
    return <EChartsRenderer option={chartConfig.option || {}} />;
  }

  // Custom engine fallback
  return (
    <div className="flex items-center justify-center h-full text-muted-foreground">
      Custom chart{chartKey ? `: ${chartKey}` : ''}
    </div>
  );
}
