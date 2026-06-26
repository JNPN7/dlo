import type { LayoutItem } from "react-grid-layout";
import type { GridConfig as RGLGridConfig } from "react-grid-layout/core";

// Re-export LayoutItem directly from react-grid-layout
export type { LayoutItem };

/**
 * Partial grid configuration for react-grid-layout.
 * All fields are optional to match the backend GridConfig schema.
 * RGL's GridConfig has required fields with defaults, but we use Partial
 * since the backend may not provide all values.
 */
export type GridConfig = Partial<RGLGridConfig>;

/**
 * Represents a dashboard resource from the API.
 */
export interface Dashboard {
  /** Display name of the dashboard */
  name: string;
  /** Unique identifier for the dashboard */
  unique_id: string;
  /** Description of the dashboard */
  description?: string;
  /** Mapping of chart keys to chart unique IDs */
  charts: Record<string, string>;
  /** Layout configuration for the grid */
  layout: LayoutItem[];
  /** Grid configuration options */
  grid_config?: GridConfig;
}

/**
 * API response format for the dashboards list endpoint.
 * Keys are the dashboard unique_id, values are Dashboard objects.
 */
export type DashboardsResponse = Record<string, Dashboard>;
