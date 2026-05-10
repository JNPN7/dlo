import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from '@copilotkit/runtime';
import { LangGraphHttpAgent } from '@copilotkit/runtime/langgraph';
import { NextRequest } from 'next/server';

const BASE_URL = process.env.AGENT_BASE_URL || 'http://localhost:6364';
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

// Cache for agent names
let cachedAgents: string[] = [];
let cacheTimestamp: number = 0;

async function fetchAgents(): Promise<string[]> {
  const now = Date.now();

  // Return cached agents if still valid
  if (cachedAgents.length > 0 && (now - cacheTimestamp) < CACHE_TTL_MS) {
    return cachedAgents;
  }

  try {
    const response = await fetch(`${BASE_URL}/api/agents`);
    if (!response.ok) return cachedAgents; // Return stale cache on error
    const agents = await response.json();

    // Update cache
    cachedAgents = agents;
    cacheTimestamp = now;

    return agents;
  } catch {
    return cachedAgents; // Return stale cache on error
  }
}

export const POST = async (req: NextRequest) => {
  const agentNames = await fetchAgents();

  const agents: Record<string, LangGraphHttpAgent> = {};

  agentNames.forEach((name, index) => {
    const agent = new LangGraphHttpAgent({
      url: `${BASE_URL}/api/agents/${name}`,
    });
    agents[name] = agent;
    // First agent becomes the default
    if (index === 0) {
      agents['default'] = agent;
    }
  });

  const runtime = new CopilotRuntime({ agents });

  const serviceAdapter = new ExperimentalEmptyAdapter();

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: '/copilotkit',
  });

  return handleRequest(req);
}
