"use client";

import { useQuery, useQueries } from "@tanstack/react-query";
import { fetchDashboards, fetchChartConfig } from "@/lib/api";
import type { ChartConfig } from "@/types/chart";

/**
 * Hook to fetch and manage the list of available dashboards.
 * Uses React Query for caching and automatic refetching.
 */
export function useDashboards() {
  const {
    data: dashboards = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["dashboards"],
    queryFn: fetchDashboards,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return {
    dashboards,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}

/**
 * Hook to fetch chart configurations for a dashboard in parallel.
 * Uses React Query's useQueries to fetch multiple chart configs simultaneously.
 *
 * @param chartMapping - Object mapping chart keys to chart unique IDs, or null to skip fetching
 * @returns Object containing chartConfigs (keyed by chart key), loading state, and errors
 */
export function useDashboardCharts(chartMapping: Record<string, string> | null) {
  const chartEntries = chartMapping ? Object.entries(chartMapping) : [];

  const results = useQueries({
    queries: chartEntries.map(([key, chartId]) => ({
      queryKey: ["chartConfig", chartId],
      queryFn: () => fetchChartConfig(chartId),
      enabled: !!chartId,
      staleTime: 1000 * 60 * 5, // 5 minutes
    })),
  });

  // Combine results into a map keyed by chart key
  const chartConfigs: Record<string, ChartConfig> = {};
  const errors: Error[] = [];

  chartEntries.forEach(([key], index) => {
    const result = results[index];
    if (result.data) {
      chartConfigs[key] = result.data as ChartConfig;
    }
    if (result.error) {
      errors.push(result.error as Error);
    }
  });

  const isLoading = results.some((r) => r.isLoading);
  const isAllLoaded = results.every((r) => !r.isLoading);

  return {
    chartConfigs,
    isLoading,
    isAllLoaded,
    errors: errors.length > 0 ? errors : null,
    // Individual loading states for each chart
    loadingStates: Object.fromEntries(
      chartEntries.map(([key], index) => [key, results[index].isLoading])
    ),
  };
}
