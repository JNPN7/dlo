import { Skeleton } from '@/components/ui/skeleton';

export type ChartSkeletonVariant = 'card' | 'full' | 'minimal';

export interface ChartSkeletonProps {
  /** 
   * Skeleton display variant:
   * - 'card': Skeleton with header bar (for grid items)
   * - 'full': Full-height centered skeleton (for standalone display)
   * - 'minimal': Simple inline skeleton
   */
  variant?: ChartSkeletonVariant;
}

/**
 * Reusable skeleton component for chart loading states.
 * Provides consistent loading UI across different chart contexts.
 */
export function ChartSkeleton({ variant = 'card' }: ChartSkeletonProps) {
  if (variant === 'minimal') {
    return <Skeleton className="h-full w-full rounded" />;
  }

  if (variant === 'full') {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-[400px] w-full max-w-3xl rounded-lg" />
      </div>
    );
  }

  // Default: 'card' variant
  return (
    <div className="h-full w-full flex flex-col bg-card rounded-lg border shadow-sm overflow-hidden">
      <div className="px-3 py-2 border-b bg-muted/30 flex-shrink-0">
        <Skeleton className="h-4 w-24" />
      </div>
      <div className="flex-1 min-h-0 p-2 flex items-center justify-center">
        <Skeleton className="h-full w-full rounded" />
      </div>
    </div>
  );
}
