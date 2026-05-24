// Agent mode matching Python AgentMode enum
export type AgentMode = "primary" | "subagent";

// Filesystem permission structure
export interface FilesystemPermission {
  type: string;
  path?: string;
}

// Agent definition matching Python Agent dataclass
export interface Agent {
  name: string;
  description: string;
  mode: AgentMode;
  model: string;
  prompt: string;
  temperature?: number;
  permissions: FilesystemPermission[];
  subagents: string[];
  skills: string[];
  tools: string[];
  base_dir?: string;
}

// Agent manifest matching Python AgentManifest dataclass
export interface AgentManifest {
  root_dir: string;
  base_dir: string;
  agents: Record<string, Agent>;
}

// Resolved agent with actual subagent objects (for UI convenience)
export interface ResolvedAgent extends Agent {
  resolvedSubagents: ResolvedAgent[];
}
