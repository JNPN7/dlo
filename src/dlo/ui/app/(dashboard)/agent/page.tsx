"use client";

import { useState, useEffect } from "react";
import { Bot, ChevronDown, MessageSquareOff } from "lucide-react";
import { useDefaultRenderTool } from "@copilotkit/react-core/v2";
import { CopilotChat } from "@copilotkit/react-core/v2";
import { Header } from "@/components/layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAgents } from "@/hooks";

// FIXME: The agent switch is not working fine, the histroy is getting messed up
// and when switching the agent the it starts with new chat
// but when we start chat old conversation shows up

/**
 * Formats an agent name for display.
 * e.g., "data_metadata" -> "Data Metadata"
 */
function formatAgentName(name: string): string {
  return name
    .split(/[_-]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

function EmptyAgentsState() {
  return (
    <div className="flex flex-1 items-center justify-center p-8">
      <Card className="w-full max-w-md text-center py-12">
        <CardContent className="space-y-4">
          <div className="flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <MessageSquareOff className="h-8 w-8 text-muted-foreground" />
            </div>
          </div>
          <h2 className="text-xl font-semibold">No Agents Available</h2>
          <p className="text-muted-foreground max-w-sm mx-auto">
            There are no agents configured for chat at this time. Please contact
            your administrator to set up AI agents.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

interface AgentSelectorProps {
  agents: string[];
  selectedAgent: string | null;
  onSelect: (agent: string) => void;
  isLoading: boolean;
}

function AgentSelector({ agents, selectedAgent, onSelect, isLoading }: AgentSelectorProps) {
  if (isLoading) {
    return <Skeleton className="h-9 w-40" />;
  }

  if (agents.length === 0) {
    return (
      <Button variant="outline" disabled>
        <Bot className="h-4 w-4 mr-2" />
        No agents
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="min-w-[180px] justify-between">
          <span className="flex items-center">
            <Bot className="h-4 w-4 mr-2" />
            {selectedAgent ? formatAgentName(selectedAgent) : "Select agent"}
          </span>
          <ChevronDown className="h-4 w-4 ml-2 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[200px]">
        <DropdownMenuLabel>Available Agents</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {agents.map((agent) => (
          <DropdownMenuItem
            key={agent}
            onClick={() => onSelect(agent)}
            className={selectedAgent === agent ? "bg-accent" : ""}
          >
            <Bot className="h-4 w-4 mr-2" />
            {formatAgentName(agent)}
            {selectedAgent === agent && (
              <span className="ml-auto text-xs text-muted-foreground">Active</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

interface AgentChatInstanceProps {
  agentId: string;
  isActive: boolean;
}

function AgentChatInstance({ agentId, isActive }: AgentChatInstanceProps) {
  useDefaultRenderTool({
    render: ({ name, status, result }) => (
      <details>
        <summary>
          {status === "complete" ? `Called ${name}` : `Calling ${name}`}
        </summary>
        <p>Status: {status}</p>
        <p>Result: {JSON.stringify(result)}</p>
      </details>
    ),
  });

  return (
    <div
      className={`h-full ${isActive ? "block" : "hidden"}`}
      aria-hidden={!isActive}
    >
      <CopilotChat labels={{}} agentId={agentId} />
    </div>
  );
}

export default function AgentPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  // Track which agents have been initialized (visited at least once)
  const [initializedAgents, setInitializedAgents] = useState<string[]>([]);
  const { agents, isLoading, error, refetch } = useAgents();

  // Auto-select first agent when agents load
  useEffect(() => {
    if (!selectedAgent && agents.length > 0) {
      setSelectedAgent(agents[0]);
    }
  }, [agents, selectedAgent]);

  // Add selected agent to initialized list when it changes
  useEffect(() => {
    if (selectedAgent && !initializedAgents.includes(selectedAgent)) {
      setInitializedAgents((prev) => [...prev, selectedAgent]);
    }
  }, [selectedAgent, initializedAgents]);

  // Error state
  if (error) {
    return (
      <div className="flex flex-col h-full">
        <Header
          title="Agent Chat"
          description="AI-powered conversation"
          actions={
            <AgentSelector
              agents={[]}
              selectedAgent={null}
              onSelect={setSelectedAgent}
              isLoading={false}
            />
          }
        />
        <div className="flex flex-1 items-center justify-center p-8">
          <Card className="w-full max-w-md">
            <CardContent className="pt-6 space-y-4">
              <h3 className="text-lg font-semibold text-destructive">Error Loading Agents</h3>
              <p className="text-muted-foreground">{error.message}</p>
              <Button onClick={() => refetch()} variant="outline">
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // No agents available (after loading)
  if (!isLoading && agents.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <Header
          title="Agent Chat"
          description="AI-powered conversation"
          onRefresh={() => refetch()}
          isLoading={isLoading}
          actions={
            <AgentSelector
              agents={agents}
              selectedAgent={selectedAgent}
              onSelect={setSelectedAgent}
              isLoading={isLoading}
            />
          }
        />
        <EmptyAgentsState />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Agent Chat"
        description={
          selectedAgent
            ? `Chatting with ${formatAgentName(selectedAgent)}`
            : "Select an agent to start chatting"
        }
        onRefresh={() => refetch()}
        isLoading={isLoading}
        actions={
          <AgentSelector
            agents={agents}
            selectedAgent={selectedAgent}
            onSelect={setSelectedAgent}
            isLoading={isLoading}
          />
        }
      />
      <div className="flex-1 overflow-hidden">
        {/* Render all initialized agent chat instances, show/hide based on selection */}
        {initializedAgents.map((agent) => (
          <AgentChatInstance
            key={agent}
            agentId={agent}
            isActive={agent === selectedAgent}
          />
        ))}

        {/* Show placeholder if no agent selected yet */}
        {!selectedAgent && (
          <div className="flex flex-1 items-center justify-center p-8 h-full">
            <Card className="w-full max-w-md text-center py-12">
              <CardContent className="space-y-4">
                <div className="flex justify-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-8 w-8 text-primary" />
                  </div>
                </div>
                <h2 className="text-xl font-semibold">Select an Agent</h2>
                <p className="text-muted-foreground max-w-sm mx-auto">
                  Choose an agent from the dropdown above to start a conversation.
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
