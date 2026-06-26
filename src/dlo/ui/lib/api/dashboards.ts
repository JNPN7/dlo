import type { Dashboard, DashboardsResponse } from "@/types/dashboard";

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
 * Fetch the list of all dashboards from the API.
 * Returns an array of Dashboard objects (converted from the key-value response).
 * Charts should be fetched separately using fetchChartConfig from the charts API.
 */
export async function fetchDashboards(): Promise<Dashboard[]> {
  const response = await fetch(`${API_BASE}/dashboards`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to fetch dashboards");
  }

  const data: DashboardsResponse = await response.json();
  // Convert the key-value object to an array of dashboards
  return Object.values(data);
}

export { ApiError };
