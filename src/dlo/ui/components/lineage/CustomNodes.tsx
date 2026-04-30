"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { Database, Box } from "lucide-react";
import { cn } from "@/lib/utils";

interface SourceNodeData {
  label: string;
  resourceType: "source";
  description?: string;
  tags: string[];
  columnCount: number;
}

interface SourceNodeProps {
  data: SourceNodeData;
  selected?: boolean;
}

export const SourceNode = memo(({ data, selected }: SourceNodeProps) => {
  return (
    <div
      className={cn(
        "px-4 py-3 rounded-lg border-2 bg-card shadow-sm min-w-[150px] transition-all",
        selected
          ? "border-primary shadow-lg ring-2 ring-primary/20"
          : "border-blue-300 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-600"
      )}
    >
      <Handle
        type="source"
        position={Position.Right}
        className="!bg-blue-500 !w-3 !h-3 !border-2 !border-white dark:!border-slate-800"
      />
      <div className="flex items-center gap-2">
        <div className="flex h-6 w-6 items-center justify-center rounded bg-blue-100 dark:bg-blue-900">
          <Database className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <div className="font-medium text-sm text-foreground">{data.label}</div>
          <div className="text-xs text-muted-foreground">{data.columnCount} columns</div>
        </div>
      </div>
    </div>
  );
});

SourceNode.displayName = "SourceNode";

interface ModelNodeData {
  label: string;
  resourceType: "model";
  modelType?: "materialized" | "view" | "ephemeral";
  description?: string;
  tags: string[];
  columnCount: number;
  schedule?: string;
}

interface ModelNodeProps {
  data: ModelNodeData;
  selected?: boolean;
}

export const ModelNode = memo(({ data, selected }: ModelNodeProps) => {
  const typeColors = {
    materialized: {
      border: selected
        ? "border-primary"
        : "border-emerald-300 dark:border-emerald-700 hover:border-emerald-400 dark:hover:border-emerald-600",
      bg: "bg-emerald-100 dark:bg-emerald-900",
      icon: "text-emerald-600 dark:text-emerald-400",
      handle: "!bg-emerald-500",
    },
    view: {
      border: selected
        ? "border-primary"
        : "border-amber-300 dark:border-amber-700 hover:border-amber-400 dark:hover:border-amber-600",
      bg: "bg-amber-100 dark:bg-amber-900",
      icon: "text-amber-600 dark:text-amber-400",
      handle: "!bg-amber-500",
    },
    ephemeral: {
      border: selected
        ? "border-primary"
        : "border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600",
      bg: "bg-slate-100 dark:bg-slate-900",
      icon: "text-slate-600 dark:text-slate-400",
      handle: "!bg-slate-500",
    },
  };

  const colors = typeColors[data.modelType || "materialized"];

  return (
    <div
      className={cn(
        "px-4 py-3 rounded-lg border-2 bg-card shadow-sm min-w-[150px] transition-all",
        colors.border,
        selected && "shadow-lg ring-2 ring-primary/20"
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className={cn(colors.handle, "!w-3 !h-3 !border-2 !border-white dark:!border-slate-800")}
      />
      <Handle
        type="source"
        position={Position.Right}
        className={cn(colors.handle, "!w-3 !h-3 !border-2 !border-white dark:!border-slate-800")}
      />
      <div className="flex items-center gap-2">
        <div className={cn("flex h-6 w-6 items-center justify-center rounded", colors.bg)}>
          <Box className={cn("h-3.5 w-3.5", colors.icon)} />
        </div>
        <div>
          <div className="font-medium text-sm text-foreground">{data.label}</div>
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <span>{data.modelType}</span>
            <span className="text-border">|</span>
            <span>{data.columnCount} cols</span>
          </div>
        </div>
      </div>
    </div>
  );
});

ModelNode.displayName = "ModelNode";

export const nodeTypes = {
  source: SourceNode,
  model: ModelNode,
};
