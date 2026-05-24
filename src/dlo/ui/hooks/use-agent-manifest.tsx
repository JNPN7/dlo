"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchAgentManifest } from "@/lib/api";
import type { Agent, AgentManifest, ResolvedAgent } from "@/types/agent";

/**
 * Recursively resolves subagents for an agent.
 * Handles nested subagents (subagents within subagents).
 */
function resolveSubagents(
  agent: Agent,
  allAgents: Record<string, Agent>,
  visited: Set<string> = new Set()
): ResolvedAgent {
  // Prevent circular references
  if (visited.has(agent.name)) {
    return {
      ...agent,
      resolvedSubagents: [],
    };
  }

  visited.add(agent.name);

  const resolvedSubagents: ResolvedAgent[] = agent.subagents
    .map((subagentName) => allAgents[subagentName])
    .filter((subagent): subagent is Agent => subagent !== undefined)
    .map((subagent) => resolveSubagents(subagent, allAgents, new Set(visited)));

  return {
    ...agent,
    resolvedSubagents,
  };
}

/**
 * Hook to fetch and manage agent manifest data.
 * Provides helpers for filtering and resolving agent relationships.
 */
export function useAgentManifest() {
  const {
    data: manifest,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["agent-manifest"],
    queryFn: fetchAgentManifest,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const value = useMemo(() => {
    const agents = manifest?.agents ?? {};
    const agentList = Object.values(agents);

    // Filter primary agents
    const primaryAgents = agentList.filter((agent) => agent.mode === "primary");

    // Resolve all primary agents with their nested subagents
    const resolvedPrimaryAgents = primaryAgents.map((agent) =>
      resolveSubagents(agent, agents)
    );

    // Get agent by name
    const getAgent = (name: string): Agent | undefined => agents[name];

    // Get resolved agent by name (with subagents resolved)
    const getResolvedAgent = (name: string): ResolvedAgent | undefined => {
      const agent = agents[name];
      if (!agent) return undefined;
      return resolveSubagents(agent, agents);
    };

    // Stats
    const stats = {
      totalAgents: agentList.length,
      primaryAgents: primaryAgents.length,
      subagents: agentList.filter((a) => a.mode === "subagent").length,
    };

    return {
      manifest: manifest ?? null,
      isLoading,
      error: error as Error | null,
      refetch,

      // All agents as array
      agents: agentList,

      // Primary agents only (not resolved)
      primaryAgents,

      // Primary agents with resolved subagents (for rendering hierarchy)
      resolvedPrimaryAgents,

      // Getters
      getAgent,
      getResolvedAgent,

      // Stats
      stats,
    };
  }, [manifest, isLoading, error, refetch]);

  return value;
}
