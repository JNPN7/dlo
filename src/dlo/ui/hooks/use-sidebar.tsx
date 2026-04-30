"use client";

import * as React from "react";
import { STORAGE_KEYS, DATA_ATTRIBUTES } from "@/lib/constants";

interface SidebarContextValue {
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  mounted: boolean;
}

const SidebarContext = React.createContext<SidebarContextValue | undefined>(undefined);

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  // Always start with false on server and client to avoid hydration mismatch
  const [isCollapsed, setIsCollapsedState] = React.useState(false);
  const [mounted, setMounted] = React.useState(false);

  // On mount, read the actual state from localStorage
  React.useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.SIDEBAR_COLLAPSED);
    if (stored === "true") {
      setIsCollapsedState(true);
    }
    setMounted(true);
  }, []);

  // Persist state to localStorage and update DOM attribute
  const setIsCollapsed = React.useCallback((collapsed: boolean) => {
    setIsCollapsedState(collapsed);
    localStorage.setItem(STORAGE_KEYS.SIDEBAR_COLLAPSED, String(collapsed));
    if (collapsed) {
      document.documentElement.setAttribute(DATA_ATTRIBUTES.SIDEBAR_COLLAPSED, "true");
    } else {
      document.documentElement.removeAttribute(DATA_ATTRIBUTES.SIDEBAR_COLLAPSED);
    }
  }, []);

  const toggleSidebar = React.useCallback(() => {
    setIsCollapsed(!isCollapsed);
  }, [isCollapsed, setIsCollapsed]);

  const value = React.useMemo(
    () => ({
      isCollapsed,
      setIsCollapsed,
      toggleSidebar,
      mounted,
    }),
    [isCollapsed, setIsCollapsed, toggleSidebar, mounted]
  );

  return <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>;
}

export function useSidebar() {
  const context = React.useContext(SidebarContext);
  if (context === undefined) {
    throw new Error("useSidebar must be used within a SidebarProvider");
  }
  return context;
}
