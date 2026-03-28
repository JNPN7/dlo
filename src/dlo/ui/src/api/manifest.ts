import type { Manifest } from '@/types/manifest';

const API_BASE = '/api';

class ApiError extends Error {
  status: number;
  
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

/**
 * Fetch the full manifest from the API.
 * This is the only API call - all other operations are done client-side.
 */
export async function fetchManifest(projectDir?: string): Promise<Manifest> {
  const params = projectDir ? `?project_dir=${encodeURIComponent(projectDir)}` : '';
  const response = await fetch(`${API_BASE}/manifest${params}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  return response.json();
}

export { ApiError };
