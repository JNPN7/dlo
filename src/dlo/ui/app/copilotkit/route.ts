import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from '@copilotkit/runtime';
import { LangGraphHttpAgent } from '@copilotkit/runtime/langgraph';
import { LangGraphAgent } from "@copilotkit/runtime/langgraph";
import { NextRequest } from 'next/server';

export const POST = async (req: NextRequest) => {
  const runtime = new CopilotRuntime({
    agents: {
      default: new LangGraphHttpAgent({
        url: process.env.AGENT_URL || 'http://localhost:6363/api/agents/data_metadata',
      }),
    },
  });

  const serviceAdapter = new ExperimentalEmptyAdapter();

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: '/copilotkit',
  });

  return handleRequest(req);
}
