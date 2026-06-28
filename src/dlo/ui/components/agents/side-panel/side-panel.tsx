"use client";

import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { SidePanelProps } from "./types";

/**
 * SidePanel - A non-blocking right sidebar panel
 * 
 * This panel:
 * - Sits alongside the main content (not overlaying)
 * - Shrinks the main content area when open
 * - Allows user to interact with content while panel is open
 */
export function SidePanel({
  isOpen,
  onClose,
  children,
  title,
}: SidePanelProps) {
  if (!isOpen) return null;

  return (
    <div className="h-full w-80 bg-background border-l shrink-0 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b shrink-0">
        {title && (
          <h2 className="text-sm font-medium">{title}</h2>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 ml-auto"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </Button>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          {children}
        </div>
      </ScrollArea>
    </div>
  );
}

export default SidePanel;
