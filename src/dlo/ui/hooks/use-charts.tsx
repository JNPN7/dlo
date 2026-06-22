"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchCharts, fetchChartConfig } from "@/lib/api";

/**
 * Hook to fetch and manage the list of available charts.
 * Uses React Query for caching and automatic refetching.
 */
export function useCharts() {
  const {
    data: charts = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["charts"],
    queryFn: fetchCharts,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return {
    charts,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}

/**
 * Hook to fetch the ECharts configuration for a specific chart.
 * Only fetches when chartId is provided (non-null).
 * 
 * @param chartId - The unique identifier of the chart to fetch, or null to skip fetching
 */
export function useChartConfig(chartId: string | null) {
  const {
    data: chartConfig,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["chartConfig", chartId],
    queryFn: () => fetchChartConfig(chartId!),
    enabled: !!chartId, // Only fetch when chartId is truthy
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return {
    chartConfig,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}
