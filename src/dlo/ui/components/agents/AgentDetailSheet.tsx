"u se client";

import { useState } from "react";
import {
  Bot,
  Cpu,
  Thermometer,
  FileText,
  Wrench,
  Zap,
  Shield,
  Users,
  ChevronDown,
  ChevronUp,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import type { ResolvedAgent } from "@/types/agent";

interface AgentDetailSheetProps {
  agent: ResolvedAgent | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectAgent?: (agent: ResolvedAgent) => void;
}

/**
 * Formats an agent name for display.
 */
function formatAgentName(name: string): string {
  return name
    .split(/[_-]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

/**
 * Section component for consistent styling
 */
function DetailSection({
  title,
  icon: Icon,
  children,
  emptyMessage,
  isEmpty,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
  emptyMessage?: string;
  isEmpty?: boolean;
}) {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
        <Icon className="h-4 w-4" />
        {title}
      </h4>
      {isEmpty && emptyMessage ? (
        <p className="text-sm text-muted-foreground/60 italic">{emptyMessage}</p>
      ) : (
        children
      )}
    </div>
  );
}

/**
 * Expandable prompt section
 */
function PromptSection({ prompt }: { prompt: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isLong = prompt.length > 300;

  return (
    <DetailSection title="System Prompt" icon={FileText}>
      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <div className="relative">
          <pre
            className={cn(
              "text-xs bg-muted p-3 rounded-lg overflow-hidden whitespace-pre-wrap font-mono",
              !isExpanded && isLong && "max-h-32"
            )}
          >
            {prompt}
          </pre>
          {isLong && !isExpanded && (
            <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-muted to-transparent rounded-b-lg" />
          )}
        </div>
        {isLong && (
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="w-full mt-1">
              {isExpanded ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  Show full prompt
                </>
              )}
            </Button>
          </CollapsibleTrigger>
        )}
      </Collapsible>
    </DetailSection>
  );
}

/**
 * Agent detail sheet component that displays comprehensive agent information.
 * Opens from the right side and remains persistent until closed.
 */
export function AgentDetailSheet({
  agent,
  open,
  onOpenChange,
  onSelectAgent,
}: AgentDetailSheetProps) {
  if (!agent) return null;

  const modeColors = {
    primary: "bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300",
    subagent: "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300",
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-lg p-0 flex flex-col"
        showCloseButton={false}
      >
        {/* Header */}
        <SheetHeader className="p-4 pb-0 shrink-0">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-lg shrink-0",
                  agent.mode === "primary"
                    ? "bg-purple-100 dark:bg-purple-900"
                    : "bg-blue-100 dark:bg-blue-900"
                )}
              >
                <Bot
                  className={cn(
                    "h-5 w-5",
                    agent.mode === "primary"
                      ? "text-purple-600 dark:text-purple-400"
                      : "text-blue-600 dark:text-blue-400"
                  )}
                />
              </div>
              <div className="min-w-0">
                <SheetTitle className="truncate">{formatAgentName(agent.name)}</SheetTitle>
                <SheetDescription className="flex items-center gap-2 mt-1">
                  <Badge className={modeColors[agent.mode]}>{agent.mode}</Badge>
                </SheetDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="shrink-0"
              onClick={() => onOpenChange(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>

        <Separator className="mt-4" />

        {/* Scrollable content */}
        <ScrollArea className="flex-1 min-h-0">
          <div className="p-4 space-y-6">
            {/* Description */}
            {agent.description && (
              <DetailSection title="Description" icon={FileText}>
                <p className="text-sm text-foreground">{agent.description}</p>
              </DetailSection>
            )}

            {/* Model & Temperature */}
            <div className="grid grid-cols-2 gap-4">
              <DetailSection title="Model" icon={Cpu}>
                <code className="text-xs bg-muted px-2 py-1 rounded block truncate">
                  {agent.model}
                </code>
              </DetailSection>
              <DetailSection title="Temperature" icon={Thermometer}>
                <code className="text-xs bg-muted px-2 py-1 rounded block">
                  {agent.temperature ?? "default"}
                </code>
              </DetailSection>
            </div>

            <Separator />

            {/* Subagents */}
            <DetailSection
              title={`Subagents (${agent.resolvedSubagents.length})`}
              icon={Users}
              isEmpty={agent.resolvedSubagents.length === 0}
              emptyMessage="No subagents configured"
            >
              <div className="flex flex-wrap gap-2">
                {agent.resolvedSubagents.map((subagent) => (
                  <Badge
                    key={subagent.name}
                    variant="outline"
                    className="cursor-pointer hover:bg-accent transition-colors"
                    onClick={() => onSelectAgent?.(subagent)}
                  >
                    <Bot className="h-3 w-3 mr-1" />
                    {formatAgentName(subagent.name)}
                  </Badge>
                ))}
              </div>
            </DetailSection>

            <Separator />

            {/* Tools */}
            <DetailSection
              title={`Tools (${agent.tools.length})`}
              icon={Wrench}
              isEmpty={agent.tools.length === 0}
              emptyMessage="No tools configured"
            >
              <div className="flex flex-wrap gap-2">
                {agent.tools.map((tool) => (
                  <Badge key={tool} variant="secondary">
                    {tool}
                  </Badge>
                ))}
              </div>
            </DetailSection>

            {/* Skills */}
            <DetailSection
              title={`Skills (${agent.skills.length})`}
              icon={Zap}
              isEmpty={agent.skills.length === 0}
              emptyMessage="No skills configured"
            >
              <div className="space-y-1">
                {agent.skills.map((skill) => (
                  <code
                    key={skill}
                    className="text-xs bg-muted px-2 py-1 rounded block truncate"
                  >
                    {skill}
                  </code>
                ))}
              </div>
            </DetailSection>

            <Separator />

            {/* Permissions */}
            <DetailSection
              title={`Permissions (${agent.permissions.length})`}
              icon={Shield}
              isEmpty={agent.permissions.length === 0}
              emptyMessage="No permissions configured"
            >
              <div className="space-y-1">
                {agent.permissions.map((permission, idx) => (
                  <div
                    key={idx}
                    className="text-xs bg-muted px-2 py-1.5 rounded flex items-center gap-2"
                  >
                    <Badge variant="outline" className="text-xs shrink-0">
                      {typeof permission === "string" ? "access" : permission.type}
                    </Badge>
                    <code className="truncate">
                      {typeof permission === "string" ? permission : permission.path || "all"}
                    </code>
                  </div>
                ))}
              </div>
            </DetailSection>

            <Separator />

            {/* System Prompt */}
            {agent.prompt && <PromptSection prompt={agent.prompt} />}

            {/* Base Directory */}
            {agent.base_dir && (
              <DetailSection title="Base Directory" icon={FileText}>
                <code className="text-xs bg-muted px-2 py-1 rounded block truncate">
                  {agent.base_dir}
                </code>
              </DetailSection>
            )}
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
