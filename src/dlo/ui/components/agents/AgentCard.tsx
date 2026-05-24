"use client";

import { memo, useState } from "react";
import { Bot, ChevronDown, ChevronRight, Info, Cpu, Wrench, Zap, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { ResolvedAgent } from "@/types/agent";

interface AgentCardProps {
  agent: ResolvedAgent;
  depth?: number;
  onSelectAgent: (agent: ResolvedAgent) => void;
  selectedAgentName?: string;
}

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
 * Recursive AgentCard component that renders primary agents and their nested subagents.
 * Supports infinite nesting depth with visual indentation.
 */
export const AgentCard = memo(function AgentCard({
  agent,
  depth = 0,
  onSelectAgent,
  selectedAgentName,
}: AgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasSubagents = agent.resolvedSubagents.length > 0;
  const isPrimary = agent.mode === "primary";
  const isSelected = selectedAgentName === agent.name;

  // Color schemes based on agent type and depth
  const getColorScheme = () => {
    if (isPrimary) {
      return {
        border: isSelected
          ? "border-primary ring-2 ring-primary/20"
          : "border-purple-300 dark:border-purple-700 hover:border-purple-400 dark:hover:border-purple-600",
        bg: "bg-purple-50 dark:bg-purple-950/30",
        iconBg: "bg-purple-100 dark:bg-purple-900",
        iconColor: "text-purple-600 dark:text-purple-400",
      };
    }
    // Subagent colors vary by depth for visual hierarchy
    const subagentColors = [
      {
        border: isSelected
          ? "border-primary ring-2 ring-primary/20"
          : "border-blue-300 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-600",
        bg: "bg-blue-50/50 dark:bg-blue-950/20",
        iconBg: "bg-blue-100 dark:bg-blue-900",
        iconColor: "text-blue-600 dark:text-blue-400",
      },
      {
        border: isSelected
          ? "border-primary ring-2 ring-primary/20"
          : "border-teal-300 dark:border-teal-700 hover:border-teal-400 dark:hover:border-teal-600",
        bg: "bg-teal-50/50 dark:bg-teal-950/20",
        iconBg: "bg-teal-100 dark:bg-teal-900",
        iconColor: "text-teal-600 dark:text-teal-400",
      },
      {
        border: isSelected
          ? "border-primary ring-2 ring-primary/20"
          : "border-cyan-300 dark:border-cyan-700 hover:border-cyan-400 dark:hover:border-cyan-600",
        bg: "bg-cyan-50/50 dark:bg-cyan-950/20",
        iconBg: "bg-cyan-100 dark:bg-cyan-900",
        iconColor: "text-cyan-600 dark:text-cyan-400",
      },
    ];
    return subagentColors[(depth - 1) % subagentColors.length];
  };

  const colors = getColorScheme();

  // Calculate stats for the agent
  const toolCount = agent.tools.length;
  const skillCount = agent.skills.length;
  const permissionCount = agent.permissions.length;

  return (
    <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
      <div
        className={cn(
          "rounded-lg border-2 transition-all",
          colors.border,
          colors.bg,
          isPrimary ? "p-4" : "p-3"
        )}
      >
        {/* Agent Header */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {/* Toggle button for agents with subagents */}
            {hasSubagents && (
              <CollapsibleTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0"
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
            )}
            {/* Agent icon */}
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-lg shrink-0",
                colors.iconBg
              )}
            >
              <Bot className={cn("h-4 w-4", colors.iconColor)} />
            </div>

            {/* Agent info */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className={cn("font-medium truncate", isPrimary ? "text-base" : "text-sm")}>
                  {formatAgentName(agent.name)}
                </span>
                <Badge variant="secondary" className="text-xs shrink-0">
                  {agent.mode}
                </Badge>
              </div>
              {agent.description && (
                <p className="text-xs text-muted-foreground truncate mt-0.5">
                  {agent.description}
                </p>
              )}
            </div>
          </div>

          {/* Action buttons and stats */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Quick stats badges */}
            <div className="hidden sm:flex items-center gap-1.5">
              {toolCount > 0 && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Badge variant="outline" className="text-xs gap-1 py-0.5">
                      <Wrench className="h-3 w-3" />
                      {toolCount}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>{toolCount} tools</TooltipContent>
                </Tooltip>
              )}
              {skillCount > 0 && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Badge variant="outline" className="text-xs gap-1 py-0.5">
                      <Zap className="h-3 w-3" />
                      {skillCount}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>{skillCount} skills</TooltipContent>
                </Tooltip>
              )}
              {permissionCount > 0 && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Badge variant="outline" className="text-xs gap-1 py-0.5">
                      <Shield className="h-3 w-3" />
                      {permissionCount}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>{permissionCount} permissions</TooltipContent>
                </Tooltip>
              )}
            </div>

            {/* Model badge */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge variant="outline" className="text-xs gap-1 py-0.5 hidden md:flex">
                  <Cpu className="h-3 w-3" />
                  <span className="max-w-[80px] truncate">{agent.model}</span>
                </Badge>
              </TooltipTrigger>
              <TooltipContent>{agent.model}</TooltipContent>
            </Tooltip>

            {/* Info button */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => onSelectAgent(agent)}
                >
                  <Info className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>View details</TooltipContent>
            </Tooltip>
          </div>
        </div>

        {/* Subagents (collapsible) */}
        {hasSubagents && (
          <CollapsibleContent>
            <div className="mt-4 ml-7 flex flex-wrap gap-3">
              {agent.resolvedSubagents.map((subagent) => (
                <div key={subagent.name} className="min-w-[280px] flex-1 max-w-md">
                  <AgentCard
                    agent={subagent}
                    depth={depth + 1}
                    onSelectAgent={onSelectAgent}
                    selectedAgentName={selectedAgentName}
                  />
                </div>
              ))}
            </div>
          </CollapsibleContent>
        )}
      </div>
    </Collapsible>
  );
});
