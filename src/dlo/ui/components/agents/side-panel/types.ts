/**
 * Side Panel component types
 */

export type TodoStatus = "pending" | "in_progress" | "completed" | "cancelled";


export interface TodoItem {
  id: string;
  content: string;
  status: TodoStatus;
}

export interface SidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
}

export interface TodoListProps {
  todos: TodoItem[];
}

export interface FloatingPanelButtonProps {
  onClick: () => void;
  className?: string;
}
