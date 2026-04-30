"use client";

import * as React from "react";

const SIDEBAR_STORAGE_KEY = "sidebar-collapsed";

interface SidebarContextValue {
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
}

const SidebarContext = React.createContext<SidebarContextValue | undefined>(undefined);

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const [isCollapsed, setIsCollapsedState] = React.useState(false);
  const [isHydrated, setIsHydrated] = React.useState(false);

  // Load persisted state from localStorage on mount (client-side only)
  React.useEffect(() => {
    const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY);
    if (stored !== null) {
      setIsCollapsedState(stored === "true");
    }
    setIsHydrated(true);
  }, []);

  // Persist state to localStorage whenever it changes
  const setIsCollapsed = React.useCallback((collapsed: boolean) => {
    setIsCollapsedState(collapsed);
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(collapsed));
  }, []);

  const toggleSidebar = React.useCallback(() => {
    setIsCollapsed(!isCollapsed);
  }, [isCollapsed, setIsCollapsed]);

  // Prevent hydration mismatch by returning consistent initial state
  const value = React.useMemo(
    () => ({
      isCollapsed: isHydrated ? isCollapsed : false,
      setIsCollapsed,
      toggleSidebar,
    }),
    [isCollapsed, isHydrated, setIsCollapsed, toggleSidebar]
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
