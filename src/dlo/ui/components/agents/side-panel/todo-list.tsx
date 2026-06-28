"use client";

import { Circle, Loader2, Check, X } from "lucide-react";
import { cn } from "@/lib/utils";
import type { TodoListProps, TodoStatus } from "./types";

/**
 * Returns the status indicator icon and color
 */
function getStatusIndicator(status: TodoStatus): {
  icon: React.ReactNode;
  className: string;
} {
  switch (status) {
    case "completed":
      return {
        icon: <Check className="h-3.5 w-3.5" />,
        className: "text-emerald-500",
      };
    case "in_progress":
      return {
        icon: <Loader2 className="h-3.5 w-3.5 animate-spin" />,
        className: "text-blue-500",
      };
    case "cancelled":
      return {
        icon: <X className="h-3.5 w-3.5" />,
        className: "text-red-500",
      };
    case "pending":
    default:
      return {
        icon: <Circle className="h-3.5 w-3.5" />,
        className: "text-muted-foreground",
      };
  }
}

/**
 * TodoList - Simple list of todos with status indicators
 */
export function TodoList({ todos }: TodoListProps) {
  if (todos.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        No todos yet
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {todos.map((todo) => {
        const indicator = getStatusIndicator(todo.status);
        const isDone = todo.status === "completed" || todo.status === "cancelled";

        return (
          <li
            key={todo.id}
            className="flex items-start gap-2 py-1.5"
          >
            <span className={cn("mt-0.5 shrink-0", indicator.className)}>
              {indicator.icon}
            </span>
            <span
              className={cn(
                "text-sm",
                isDone && "line-through text-muted-foreground"
              )}
            >
              {todo.content}
            </span>
          </li>
        );
      })}
    </ul>
  );
}

export default TodoList;
