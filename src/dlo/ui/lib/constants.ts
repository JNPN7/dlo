/**
 * Storage keys for localStorage persistence
 */
export const STORAGE_KEYS = {
  /** Theme preference: "light" | "dark" | "system" */
  THEME: "dlo-ui-theme",
  /** Sidebar collapsed state: "true" | "false" */
  SIDEBAR_COLLAPSED: "sidebar-collapsed",
} as const;

/**
 * Data attributes for HTML element state management
 * Used by blocking scripts to prevent flash of incorrect state
 */
export const DATA_ATTRIBUTES = {
  /** Set on <html> when sidebar is collapsed */
  SIDEBAR_COLLAPSED: "data-sidebar-collapsed",
} as const;
