"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Database,
  Box,
  GitBranch,
  BarChart3,
  LayoutDashboard,
  Network,
  Search,
  ChevronLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useSidebar } from "@/hooks";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Sources", href: "/sources", icon: Database },
  { name: "Models", href: "/models", icon: Box },
  { name: "Relationships", href: "/relationships", icon: GitBranch },
  { name: "Metrics", href: "/metrics", icon: BarChart3 },
  { name: "Lineage", href: "/lineage", icon: Network },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isCollapsed, setIsCollapsed, toggleSidebar, mounted } = useSidebar();
  const [isHoveringItem, setIsHoveringItem] = React.useState(false);

  // Handle click on sidebar background when collapsed - expand if not hovering an item
  const handleSidebarClick = (e: React.MouseEvent) => {
    if (isCollapsed && !isHoveringItem) {
      // Only toggle if clicked directly on the sidebar container, not on interactive elements
      const target = e.target as HTMLElement;
      const isInteractiveElement = target.closest("a, button");
      if (!isInteractiveElement) {
        setIsCollapsed(false);
      }
    }
  };

  // Before mount, use CSS classes to control visibility (via data-sidebar-collapsed attribute)
  // After mount, use React state for dynamic control
  const showCollapsed = mounted ? isCollapsed : false;

  return (
    <div
      className={cn(
        "sidebar-container flex h-full flex-col border-r border-border bg-sidebar-background transition-all duration-300 ease-in-out",
        // After mount, React controls the width; before mount, CSS handles it via data attribute
        mounted && (isCollapsed ? "w-16 cursor-e-resize" : "w-64"),
        !mounted && "w-64" // Default for SSR, CSS will override if data-sidebar-collapsed is set
      )}
      onClick={handleSidebarClick}
    >
      {/* Logo and Toggle */}
      <div
        className={cn(
          "flex h-16 items-center border-b border-border",
          showCollapsed ? "justify-center px-2" : "justify-between px-4"
        )}
      >
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg">
            <img
              src="/assets/favicon.svg"
              className="h-6 w-6 text-primary-foreground"
              alt="DLO"
            />
          </div>
          {/* Expanded: show title */}
          <span
            className={cn(
              "text-xl font-bold text-sidebar-foreground",
              showCollapsed && "hidden",
              !mounted && "sidebar-expanded-only"
            )}
          >
            DLO
          </span>
        </div>
        {/* Expanded: show collapse button */}
        <div
          className={cn(
            showCollapsed && "hidden",
            !mounted && "sidebar-expanded-only"
          )}
        >
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 cursor-w-resize"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleSidebar();
                }}
              >
                <ChevronLeft className="h-4 w-4" />
                <span className="sr-only">Collapse sidebar</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">Collapse sidebar</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Search */}
      <div className={cn("py-4", showCollapsed ? "px-2" : "px-4")}>
        {/* Collapsed search */}
        <div
          className={cn(
            !showCollapsed && "hidden",
            !mounted && "sidebar-collapsed-only hidden"
          )}
        >
          <Tooltip>
            <TooltipTrigger asChild>
              <Link
                href="/search"
                className={cn(
                  "flex h-10 w-full items-center justify-center rounded-lg border border-input bg-background text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
                  pathname === "/search" && "bg-accent text-accent-foreground"
                )}
                onMouseEnter={() => setIsHoveringItem(true)}
                onMouseLeave={() => setIsHoveringItem(false)}
                onClick={(e) => e.stopPropagation()}
              >
                <Search className="h-4 w-4" />
              </Link>
            </TooltipTrigger>
            <TooltipContent side="right">Search</TooltipContent>
          </Tooltip>
        </div>
        {/* Expanded search */}
        <div
          className={cn(
            showCollapsed && "hidden",
            !mounted && "sidebar-expanded-only"
          )}
        >
          <Link
            href="/search"
            className={cn(
              "flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
              pathname === "/search" && "bg-accent text-accent-foreground"
            )}
          >
            <Search className="h-4 w-4" />
            <span>Search...</span>
            <kbd className="ml-auto pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
              <span className="text-xs">/</span>
            </kbd>
          </Link>
        </div>
      </div>

      <Separator />

      {/* Navigation */}
      <ScrollArea className={cn("flex-1 py-4", showCollapsed ? "px-2" : "px-4")}>
        <nav className="flex flex-col gap-1">
          {navigation.map((item) => {
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

            return (
              <React.Fragment key={item.name}>
                {/* Collapsed nav item */}
                <div
                  className={cn(
                    !showCollapsed && "hidden",
                    !mounted && "sidebar-collapsed-only hidden"
                  )}
                >
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex h-10 w-full items-center justify-center rounded-lg transition-colors",
                          isActive
                            ? "bg-sidebar-accent text-sidebar-accent-foreground"
                            : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                        )}
                        onMouseEnter={() => setIsHoveringItem(true)}
                        onMouseLeave={() => setIsHoveringItem(false)}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <item.icon className="h-4 w-4" />
                      </Link>
                    </TooltipTrigger>
                    <TooltipContent side="right">{item.name}</TooltipContent>
                  </Tooltip>
                </div>
                {/* Expanded nav item */}
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                    showCollapsed && "hidden",
                    !mounted && "sidebar-expanded-only"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </Link>
              </React.Fragment>
            );
          })}
        </nav>
      </ScrollArea>

      {/* Footer */}
      <Separator />
      <div className={cn("p-4", showCollapsed && "px-2")}>
        {/* Collapsed footer */}
        <div
          className={cn(
            !showCollapsed && "hidden",
            !mounted && "sidebar-collapsed-only hidden"
          )}
        >
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex h-10 items-center justify-center rounded-lg bg-muted cursor-default">
                <span className="text-[10px] font-semibold text-muted-foreground">v0.0.1</span>
              </div>
            </TooltipTrigger>
            <TooltipContent side="right">Data Lineage Orchestrator v0.0.1</TooltipContent>
          </Tooltip>
        </div>
        {/* Expanded footer */}
        <div
          className={cn(
            "rounded-lg bg-muted p-3",
            showCollapsed && "hidden",
            !mounted && "sidebar-expanded-only"
          )}
        >
          <p className="text-xs text-muted-foreground">Data Lineage Orchestrator</p>
          <p className="text-xs font-medium text-foreground">v0.0.1</p>
        </div>
      </div>
    </div>
  );
}
