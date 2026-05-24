"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  type Node,
  type Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Bot, Users, ChevronDown, ChevronRight } from "lucide-react";

import { Header } from "@/components/layout";
import { AgentDetailSheet, AgentFilters, agentNodeTypes } from "@/components/agents";
import type { AgentNodeData } from "@/components/agents";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useAgentManifest } from "@/hooks";
import type { ResolvedAgent, AgentMode } from "@/types/agent";

// ============================================================================
// Layout Algorithm
// ============================================================================

function getInitialLayout(agents: ResolvedAgent[]): { x: number; y: number }[] {
  const COLS = 3;
  const NODE_WIDTH = 360;
  const NODE_HEIGHT = 140;
  const GAP_X = 80;
  const GAP_Y = 80;

  return agents.map((_, index) => ({
    x: (index % COLS) * (NODE_WIDTH + GAP_X),
    y: Math.floor(index / COLS) * (NODE_HEIGHT + GAP_Y),
  }));
}

// ============================================================================
// Loading, Error, Empty States
// ============================================================================

function LoadingState() {
  return (
    <div className="flex flex-col h-full">
      <Header title="Agent Lineage" description="Loading agents..." />
      <div className="flex-1 p-6 space-y-4">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-[500px] w-full" />
      </div>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: Error; onRetry: () => void }) {
  return (
    <div className="flex flex-col h-full">
      <Header title="Agent Lineage" description="Error loading agents" />
      <div className="flex-1 flex items-center justify-center p-6">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 space-y-4">
            <h3 className="text-lg font-semibold text-destructive">Error Loading Agents</h3>
            <p className="text-muted-foreground">{error.message}</p>
            <Button onClick={onRetry} variant="outline">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col h-full">
      <Header title="Agent Lineage" description="Agent hierarchy visualization" />
      <div className="flex-1 flex items-center justify-center p-6">
        <Card className="w-full max-w-md text-center py-12">
          <CardContent className="space-y-4">
            <div className="flex justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <Bot className="h-8 w-8 text-muted-foreground" />
              </div>
            </div>
            <h2 className="text-xl font-semibold">No Agents Found</h2>
            <p className="text-muted-foreground max-w-sm mx-auto">
              There are no agents configured in your project. Create agent configuration files
              in your .dlo, .opencode, or .claude directory to get started.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ============================================================================
// Main Page Component
// ============================================================================

export default function AgentLineagePage() {
  const { resolvedPrimaryAgents, agents, stats, isLoading, error, refetch } = useAgentManifest();

  // Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [modeFilter, setModeFilter] = useState<"all" | AgentMode>("all");
  const [modelFilter, setModelFilter] = useState("all");

  // Expansion state
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [expandedSubagents, setExpandedSubagents] = useState<Set<string>>(new Set());

  // Detail sheet state
  const [selectedAgent, setSelectedAgent] = useState<ResolvedAgent | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);

  // ReactFlow state
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Get unique models for filter dropdown
  const availableModels = useMemo(() => {
    const models = new Set(agents.map((a) => a.model));
    return Array.from(models).sort();
  }, [agents]);

  // Check if filters are active
  const hasActiveFilters = searchQuery !== "" || modeFilter !== "all" || modelFilter !== "all";

  // Filter matching function
  const matchesFilter = useCallback(
    (agent: ResolvedAgent): boolean => {
      const matchesSearch =
        searchQuery === "" ||
        agent.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesMode = modeFilter === "all" || agent.mode === modeFilter;
      const matchesModel = modelFilter === "all" || agent.model === modelFilter;
      return matchesSearch && matchesMode && matchesModel;
    },
    [searchQuery, modeFilter, modelFilter]
  );

  // Handlers
  const handleToggleExpand = useCallback((agentName: string) => {
    setExpandedAgents((prev) => {
      const next = new Set(prev);
      if (next.has(agentName)) {
        next.delete(agentName);
      } else {
        next.add(agentName);
      }
      return next;
    });
  }, []);

  const handleToggleSubagentExpand = useCallback((agentName: string) => {
    setExpandedSubagents((prev) => {
      const next = new Set(prev);
      if (next.has(agentName)) {
        next.delete(agentName);
      } else {
        next.add(agentName);
      }
      return next;
    });
  }, []);

  const handleSelectAgent = useCallback((agent: ResolvedAgent) => {
    setSelectedAgent(agent);
    setSheetOpen(true);
  }, []);

  const handleExpandAll = useCallback(() => {
    const allNames = new Set(agents.map((a) => a.name));
    setExpandedAgents(allNames);
    setExpandedSubagents(allNames);
  }, [agents]);

  const handleCollapseAll = useCallback(() => {
    setExpandedAgents(new Set());
    setExpandedSubagents(new Set());
  }, []);

  const handleClearFilters = useCallback(() => {
    setSearchQuery("");
    setModeFilter("all");
    setModelFilter("all");
  }, []);

  const handleSheetOpenChange = useCallback((open: boolean) => {
    setSheetOpen(open);
  }, []);

  // Generate nodes and edges from agents
  useEffect(() => {
    if (resolvedPrimaryAgents.length === 0) return;

    const positions = getInitialLayout(resolvedPrimaryAgents);
    const primaryAgentNames = new Set(resolvedPrimaryAgents.map((a) => a.name));

    // Create nodes
    const newNodes: Node<AgentNodeData>[] = resolvedPrimaryAgents.map((agent, index) => ({
      id: agent.name,
      type: "agent",
      position: positions[index],
      data: {
        agent,
        isExpanded: expandedAgents.has(agent.name),
        expandedSubagents,
        onToggleExpand: handleToggleExpand,
        onToggleSubagentExpand: handleToggleSubagentExpand,
        onSelectAgent: handleSelectAgent,
        isFiltered: !matchesFilter(agent),
      },
    }));

    // Create edges (parent → child when subagent is also a primary agent)
    const newEdges: Edge[] = [];
    for (const agent of resolvedPrimaryAgents) {
      for (const subagentName of agent.subagents) {
        if (primaryAgentNames.has(subagentName)) {
          newEdges.push({
            id: `${agent.name}->${subagentName}`,
            source: agent.name,
            target: subagentName,
            type: "smoothstep",
            animated: true,
            style: {
              stroke: "hsl(270, 70%, 50%)",
              strokeWidth: 2,
              strokeDasharray: "5,5",
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: "hsl(270, 70%, 50%)",
            },
          });
        }
      }
    }

    setNodes(newNodes);
    setEdges(newEdges);
  }, [
    resolvedPrimaryAgents,
    expandedAgents,
    expandedSubagents,
    matchesFilter,
    handleToggleExpand,
    handleToggleSubagentExpand,
    handleSelectAgent,
    setNodes,
    setEdges,
  ]);

  // Loading state
  if (isLoading) {
    return <LoadingState />;
  }

  // Error state
  if (error) {
    return <ErrorState error={error} onRetry={refetch} />;
  }

  // Empty state
  if (resolvedPrimaryAgents.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <Header
        title="Agent Lineage"
        description={`${stats.totalAgents} agents (${stats.primaryAgents} primary, ${stats.subagents} subagents)`}
        onRefresh={refetch}
        isLoading={isLoading}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleExpandAll}>
              <ChevronDown className="h-4 w-4 mr-1" />
              Expand All
            </Button>
            <Button variant="outline" size="sm" onClick={handleCollapseAll}>
              <ChevronRight className="h-4 w-4 mr-1" />
              Collapse All
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Badge variant="outline" className="gap-1">
              <Users className="h-3 w-3" />
              {stats.primaryAgents} Primary
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Bot className="h-3 w-3" />
              {stats.subagents} Subagents
            </Badge>
          </div>
        }
      />

      {/* Filter bar */}
      <div className="px-6 py-3 border-b border-border bg-background">
        <AgentFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          modeFilter={modeFilter}
          onModeChange={setModeFilter}
          modelFilter={modelFilter}
          onModelChange={setModelFilter}
          availableModels={availableModels}
          onClear={handleClearFilters}
          hasActiveFilters={hasActiveFilters}
        />
      </div>

      {/* ReactFlow Canvas */}
      <div className="flex-1 p-6">
        <Card className="h-full min-h-[500px]">
          <CardContent className="p-0 h-full">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              nodeTypes={agentNodeTypes}
              fitView
              fitViewOptions={{ padding: 0.3 }}
              minZoom={0.1}
              maxZoom={2}
              defaultEdgeOptions={{
                type: "smoothstep",
              }}
            >
              <Controls className="!bg-card !border-border !shadow-md" />
              <MiniMap
                nodeColor={(node) => {
                  const data = node.data as AgentNodeData;
                  if (data?.isFiltered) return "hsl(220, 10%, 70%)";
                  const agent = data?.agent;
                  if (agent?.mode === "primary") return "hsl(270, 70%, 50%)";
                  return "hsl(210, 70%, 50%)";
                }}
                className="!bg-card !border-border"
              />
              <Background
                variant={BackgroundVariant.Dots}
                gap={20}
                size={1}
                color="hsl(var(--muted-foreground) / 0.2)"
              />
            </ReactFlow>
          </CardContent>
        </Card>
      </div>

      {/* Detail Sheet */}
      <AgentDetailSheet
        agent={selectedAgent}
        open={sheetOpen}
        onOpenChange={handleSheetOpenChange}
        onSelectAgent={handleSelectAgent}
      />
    </div>
  );
}
