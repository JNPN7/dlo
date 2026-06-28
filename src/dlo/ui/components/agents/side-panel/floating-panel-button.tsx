"use client";

import { PanelRightOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { FloatingPanelButtonProps } from "./types";

/**
 * FloatingPanelButton - Circular floating action button to toggle the side panel
 */
export function FloatingPanelButton({
  onClick,
  className,
}: FloatingPanelButtonProps) {
  return (
    <Button
      onClick={onClick}
      size="icon"
      className={cn(
        "fixed bottom-6 right-6 z-30 h-12 w-12 rounded-full shadow-lg",
        className
      )}
      variant="default"
    >
      <PanelRightOpen className="h-5 w-5" />
      <span className="sr-only">Open details panel</span>
    </Button>
  );
}

export default FloatingPanelButton;
