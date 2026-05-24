"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { Bot, ChevronDown, ChevronRight, Info, Cpu, Wrench, Zap, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { ResolvedAgent } from "@/types/agent";

/**
 * Formats an agent name for display.
 * e.g., "data_metadata_agent" -> "Data Metadata Agent"
 */
function formatAgentName(name: string): string {
  return name
    .split(/[_-]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

/**
 * Truncates model name for display
 */
function formatModelName(model: string, maxLength = 16): string {
  if (model.length <= maxLength) return model;
  return model.slice(0, maxLength - 2) + "...";
}

// ============================================================================
// Subagent Card (rendered inside primary agent when expanded)
// ============================================================================

interface SubagentCardProps {
  agent: ResolvedAgent;
  onSelectAgent: (agent: ResolvedAgent) => void;
  isExpanded: boolean;
  onToggleExpand: (agentName: string) => void;
  depth?: number;
}

const SubagentCard = memo(function SubagentCard({
  agent,
  onSelectAgent,
  isExpanded,
  onToggleExpand,
  depth = 1,
}: SubagentCardProps) {
  const hasSubagents = agent.resolvedSubagents.length > 0;
  const toolCount = agent.tools.length;
  const skillCount = agent.skills.length;
  const permissionCount = agent.permissions.length;

  // Colors vary by depth
  const depthColors = [
    { border: "border-blue-300 dark:border-blue-600", bg: "bg-blue-50 dark:bg-blue-950/40" },
    { border: "border-teal-300 dark:border-teal-600", bg: "bg-teal-50 dark:bg-teal-950/40" },
    { border: "border-cyan-300 dark:border-cyan-600", bg: "bg-cyan-50 dark:bg-cyan-950/40" },
  ];
  const colors = depthColors[(depth - 1) % depthColors.length];

  return (
    <div className={cn("rounded-md border p-2", colors.border, colors.bg)}>
      {/* Row 1: Name and actions */}
      <div className="flex items-center gap-2">
        {hasSubagents && (
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5 shrink-0"
            onClick={(e) => {
              e.stopPropagation();
              onToggleExpand(agent.name);
            }}
          >
            {isExpanded ? (
              <ChevronDown className="h-3 w-3" />
            ) : (
              <ChevronRight className="h-3 w-3" />
            )}
          </Button>
        )}
        <Bot className="h-3.5 w-3.5 text-blue-500 shrink-0" />

        <span className="text-xs font-medium truncate flex-1">
          {formatAgentName(agent.name)}
        </span>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-5 w-5 shrink-0"
              onClick={(e) => {
                e.stopPropagation();
                onSelectAgent(agent);
              }}
            >
              <Info className="h-3 w-3" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>View details</TooltipContent>
        </Tooltip>
      </div>

      {/* Row 2: Model and stats */}
      <div className={cn("flex items-center gap-1.5 mt-1 text-[10px] text-muted-foreground", hasSubagents && "ml-7")}>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="flex items-center gap-1 py-0.5">
              <Cpu className="h-3 w-3" />
              <span className="truncate max-w-[100px]">{formatModelName(agent.model)}</span>
            </span>
          </TooltipTrigger>
          <TooltipContent>{agent.model}</TooltipContent>
        </Tooltip>

        {toolCount > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1 px-1 py-0.5">
                <Wrench className="h-3 w-3" />
                {toolCount}
              </span>
            </TooltipTrigger>
            <TooltipContent>{toolCount} tools</TooltipContent>
          </Tooltip>
        )}

        {skillCount > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1 px-1 py-0.5">
                <Zap className="h-3 w-3" />
                {skillCount}
              </span>
            </TooltipTrigger>
            <TooltipContent>{skillCount} skills</TooltipContent>
          </Tooltip>
        )}

        {permissionCount > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1 px-1 py-0.5">
                <Shield className="h-3 w-3" />
                {permissionCount}
              </span>
            </TooltipTrigger>
            <TooltipContent>{permissionCount} permissions</TooltipContent>
          </Tooltip>
        )}

        {hasSubagents && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1 px-1 py-0.5">
                <Bot className="h-3 w-3" />
                {agent.resolvedSubagents.length}
              </span>
            </TooltipTrigger>
            <TooltipContent>{agent.resolvedSubagents.length} subagents</TooltipContent>
          </Tooltip>
        )}
      </div>

      {/* Nested subagents */}
      {
        hasSubagents && isExpanded && (
          <div className="mt-2 flex flex-wrap gap-2">
            {agent.resolvedSubagents.map((subagent) => (
              <SubagentCard
                key={subagent.name}
                agent={subagent}
                onSelectAgent={onSelectAgent}
                isExpanded={false}
                onToggleExpand={onToggleExpand}
                depth={depth + 1}
              />
            ))}
          </div>
        )
      }
    </div >
  );
});

// ============================================================================
// Main Agent Node (ReactFlow custom node)
// ============================================================================

export interface AgentNodeData extends Record<string, unknown> {
  agent: ResolvedAgent;
  isExpanded: boolean;
  expandedSubagents: Set<string>;
  onToggleExpand: (agentName: string) => void;
  onToggleSubagentExpand: (agentName: string) => void;
  onSelectAgent: (agent: ResolvedAgent) => void;
  isFiltered: boolean;
}

interface AgentNodeProps {
  data: AgentNodeData;
  selected?: boolean;
}

export const AgentNode = memo(function AgentNode({ data, selected }: AgentNodeProps) {
  const {
    agent,
    isExpanded,
    expandedSubagents,
    onToggleExpand,
    onToggleSubagentExpand,
    onSelectAgent,
    isFiltered,
  } = data;

  const hasSubagents = agent.resolvedSubagents.length > 0;
  const isPrimary = agent.mode === "primary";
  const toolCount = agent.tools.length;
  const skillCount = agent.skills.length;
  const permissionCount = agent.permissions.length;

  const modeColors = {
    primary: "bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300",
    subagent: "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300",
  };

  return (
    <div
      className={cn(
        "rounded-lg border-2 bg-card shadow-md transition-all min-w-[320px] max-w-[400px]",
        selected
          ? "border-primary ring-2 ring-primary/20"
          : isPrimary
            ? "border-purple-400 dark:border-purple-600"
            : "border-blue-400 dark:border-blue-600",
        isFiltered && "opacity-30"
      )}
    >
      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-purple-500 !w-3 !h-3 !border-2 !border-white dark:!border-slate-800"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-purple-500 !w-3 !h-3 !border-2 !border-white dark:!border-slate-800"
      />

      {/* Header section */}
      <div className="p-3">
        {/* Row 1: Icon, Name, Mode, Toggle, Info */}
        <div className="flex items-center gap-2">
          <div
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-lg shrink-0",
              isPrimary
                ? "bg-purple-100 dark:bg-purple-900"
                : "bg-blue-100 dark:bg-blue-900"
            )}
          >
            <Bot
              className={cn(
                "h-4 w-4",
                isPrimary
                  ? "text-purple-600 dark:text-purple-400"
                  : "text-blue-600 dark:text-blue-400"
              )}
            />
          </div>

          <div className="flex-1 min-w-0">
            <span className="font-semibold text-sm truncate block">
              {formatAgentName(agent.name)}
            </span>
          </div>

          <Badge className={cn("text-xs shrink-0", modeColors[agent.mode])}>
            {agent.mode}
          </Badge>

          {hasSubagents && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleExpand(agent.name);
                  }}
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {isExpanded ? "Collapse subagents" : "Expand subagents"}
              </TooltipContent>
            </Tooltip>
          )}

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className="h-7 w-7 shrink-0"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectAgent(agent);
                }}
              >
                <Info className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>View details</TooltipContent>
          </Tooltip>
        </div>

        {/* Row 2: Model and stats */}
        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1 bg-muted px-2 py-0.5 rounded">
                <Cpu className="h-3 w-3" />
                <span className="truncate max-w-[100px]">{formatModelName(agent.model)}</span>
              </span>
            </TooltipTrigger>
            <TooltipContent>{agent.model}</TooltipContent>
          </Tooltip>

          {toolCount > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="flex items-center gap-1 bg-muted px-2 py-0.5 rounded">
                  <Wrench className="h-3 w-3" />
                  {toolCount}
                </span>
              </TooltipTrigger>
              <TooltipContent>{toolCount} tools</TooltipContent>
            </Tooltip>
          )}

          {skillCount > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="flex items-center gap-1 bg-muted px-2 py-0.5 rounded">
                  <Zap className="h-3 w-3" />
                  {skillCount}
                </span>
              </TooltipTrigger>
              <TooltipContent>{skillCount} skills</TooltipContent>
            </Tooltip>
          )}

          {permissionCount > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="flex items-center gap-1 bg-muted px-2 py-0.5 rounded">
                  <Shield className="h-3 w-3" />
                  {permissionCount}
                </span>
              </TooltipTrigger>
              <TooltipContent>{permissionCount} permissions</TooltipContent>
            </Tooltip>
          )}

          {hasSubagents && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="flex items-center gap-1 bg-muted px-2 py-0.5 rounded">
                  <Bot className="h-3 w-3" />
                  {agent.resolvedSubagents.length}
                </span>
              </TooltipTrigger>
              <TooltipContent>{agent.resolvedSubagents.length} subagents</TooltipContent>
            </Tooltip>
          )}
        </div>
      </div>

      {/* Subagents section (when expanded) */}
      {hasSubagents && isExpanded && (
        <div className="border-t border-border p-3 bg-muted/30">
          <div className="flex flex-wrap gap-2">
            {agent.resolvedSubagents.map((subagent) => (
              <SubagentCard
                key={subagent.name}
                agent={subagent}
                onSelectAgent={onSelectAgent}
                isExpanded={expandedSubagents.has(subagent.name)}
                onToggleExpand={onToggleSubagentExpand}
                depth={1}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

AgentNode.displayName = "AgentNode";

// Export node types for ReactFlow
export const agentNodeTypes = {
  agent: AgentNode,
};
