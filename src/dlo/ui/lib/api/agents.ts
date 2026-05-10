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
 * Fetch available agents from the API.
 * Returns an array of agent names.
 */
export async function fetchAgents(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/agents`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || "Failed to fetch agents");
  }

  return response.json();
}

export { ApiError };
