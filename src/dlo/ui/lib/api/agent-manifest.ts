import type { AgentManifest } from "@/types/agent";

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
 * Fetch agent manifest from the API.
 * Returns the complete agent manifest with all agents.
 */
export async function fetchAgentManifest(): Promise<AgentManifest> {
  const response = await fetch(`${API_BASE}/agents-manifest`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to fetch agent manifest");
  }

  return response.json();
}

export { ApiError };
