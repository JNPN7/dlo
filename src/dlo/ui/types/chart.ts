/**
 * Represents a chart resource from the API.
 */
export interface Chart {
  /** Display name of the chart */
  name: string;
  /** Unique identifier for the chart */
  unique_id: string;
  /** Description of what the chart shows */
  description: string;
}

/**
 * Represents a chart config from the API.
 */
export interface ChartConfig {
  /** Engine of chart to render*/
  engine: "echarts" | "custom";
  /** Option (config) of chart*/
  option: Record<string, any>;
}

/**
 * API response format for the charts list endpoint.
 * Keys are the chart unique_id, values are Chart objects.
 */
export type ChartsResponse = Record<string, Chart>;
