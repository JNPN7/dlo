import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/v2/styles.css";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit runtimeUrl="/copilotkit">
      {children}
    </CopilotKit>
  )
} 
