"use client";

import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { AgentMode } from "@/types/agent";

interface AgentFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  modeFilter: "all" | AgentMode;
  onModeChange: (mode: "all" | AgentMode) => void;
  modelFilter: string;
  onModelChange: (model: string) => void;
  availableModels: string[];
  onClear: () => void;
  hasActiveFilters: boolean;
}

export function AgentFilters({
  searchQuery,
  onSearchChange,
  modeFilter,
  onModeChange,
  modelFilter,
  onModelChange,
  availableModels,
  onClear,
  hasActiveFilters,
}: AgentFiltersProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search agents..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9 w-[180px] h-9"
        />
      </div>

      {/* Mode filter dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="h-9">
            Mode: {modeFilter === "all" ? "All" : modeFilter}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem onClick={() => onModeChange("all")}>
            All
            {modeFilter === "all" && (
              <span className="ml-auto text-xs text-muted-foreground">Active</span>
            )}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => onModeChange("primary")}>
            Primary
            {modeFilter === "primary" && (
              <span className="ml-auto text-xs text-muted-foreground">Active</span>
            )}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => onModeChange("subagent")}>
            Subagent
            {modeFilter === "subagent" && (
              <span className="ml-auto text-xs text-muted-foreground">Active</span>
            )}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Model filter dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="h-9 max-w-[150px]">
            <span className="truncate">
              Model: {modelFilter === "all" ? "All" : modelFilter}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="max-h-[300px] overflow-y-auto">
          <DropdownMenuItem onClick={() => onModelChange("all")}>
            All
            {modelFilter === "all" && (
              <span className="ml-auto text-xs text-muted-foreground">Active</span>
            )}
          </DropdownMenuItem>
          {availableModels.map((model) => (
            <DropdownMenuItem key={model} onClick={() => onModelChange(model)}>
              <span className="truncate max-w-[200px]">{model}</span>
              {modelFilter === model && (
                <span className="ml-auto text-xs text-muted-foreground">Active</span>
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Clear filters button */}
      {hasActiveFilters && (
        <Button variant="ghost" size="sm" className="h-9" onClick={onClear}>
          <X className="h-4 w-4 mr-1" />
          Clear
        </Button>
      )}
    </div>
  );
}
