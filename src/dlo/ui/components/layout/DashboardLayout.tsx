"use client";

import { Sidebar } from "./Sidebar";
import { TooltipProvider } from "@/components/ui/Tooltip";
import { SidebarProvider } from "@/hooks";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <SidebarProvider>
      <TooltipProvider>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </TooltipProvider>
    </SidebarProvider>
  );
}
