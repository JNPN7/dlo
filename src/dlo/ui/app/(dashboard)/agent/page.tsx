"use client";

import { useDefaultRenderTool } from "@copilotkit/react-core/v2";
import { CopilotChat } from '@copilotkit/react-core/v2';

export default function Page() {
  useDefaultRenderTool({
    render: ({ name, status, result }) => (
      <details>
        <summary>
          {status === "complete" ? `Called ${name}` : `Calling ${name}`}
        </summary>
        <p>Status: {status}</p>
        <p>Result: {JSON.stringify(result)}</p>
      </details>
    )
  })

  return (
    <CopilotChat labels={{}} />
  );
}
