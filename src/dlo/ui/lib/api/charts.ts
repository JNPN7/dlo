import type { Chart, ChartsResponse } from "@/types/chart";

const API_BASE = "/api";

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

/**
 * Fetch the list of all charts from the API.
 * Returns an array of Chart objects (converted from the key-value response).
 */
export async function fetchCharts(): Promise<Chart[]> {
  const response = await fetch(`${API_BASE}/charts`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to fetch charts");
  }

  const data: ChartsResponse = await response.json();
  // Convert the key-value object to an array of charts
  return Object.values(data);
}

/**
 * Fetch the ECharts configuration for a specific chart.
 * @param chartId - The unique identifier of the chart
 * @returns The ECharts option configuration object
 */
export async function fetchChartConfig(chartId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/charts/${encodeURIComponent(chartId)}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || `Failed to fetch chart config for ${chartId}`);
  }

  return response.json();
}

export { ApiError };
