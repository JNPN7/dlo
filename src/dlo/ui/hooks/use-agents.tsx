"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAgents } from "@/lib/api";

/**
 * Hook to fetch and manage available agents.
 * Uses React Query for caching and automatic refetching.
 */
export function useAgents() {
  const {
    data: agents = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return {
    agents,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}
