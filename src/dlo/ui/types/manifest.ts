// Enums matching Python models
export type ResourceType = "source" | "model" | "relationship" | "metric" | "code";
export type ColumnCategory = "dimension" | "measure";
export type StorageType = "table" | "csv";
export type ModelType = "materialized" | "view" | "ephemeral";
export type CodeType = "sql";

// Profiling metrics for columns
export interface ProfilingMetrics {
  count?: number;
  null_count?: number;
  distinct_count?: number;
}

// Column definition
export interface Column {
  name: string;
  type: string;
  category?: ColumnCategory;
  description?: string;
  tags?: string[];
  profiling_metrics?: ProfilingMetrics;
  sample_data?: (string | number)[];
}

// Source details
export interface SourceDetails {
  full_name: string;
  type: StorageType;
}

// Model details
export interface ModelDetails {
  full_name?: string;
  type: StorageType;
}

// Dependency tracking
export interface DependsOn {
  nodes: string[];
}

// Injected CTE for compiled queries
export interface InjectedCTE {
  id: string;
  sql: string;
}

// Base resource fields
export interface BaseResource {
  name: string;
  file_path: string;
  resource_type: ResourceType;
  description?: string;
  tags?: string[];
  unique_id?: string;
}

// Source resource
export interface Source extends BaseResource {
  resource_type: "source";
  details: SourceDetails;
  columns: Column[];
  connection?: string;
  primary_key?: string[];
  unique_keys?: string[][];
}

// Model resource
export interface Model extends BaseResource {
  resource_type: "model";
  type: ModelType;
  columns: Column[];
  details?: ModelDetails;
  schedule?: string;
  primary_key?: string[];
  unique_keys?: string[][];
  raw_code?: string;
  code_path?: string;
  // Compiled resource fields
  sources: string[];
  compiled_path?: string;
  compiled_code?: string;
  compiled: boolean;
  depends_on: DependsOn;
  extra_ctes: InjectedCTE[];
  // Scheduled resource fields
  schedule_depends_on: DependsOn;
}

// Relationship resource
export interface Relationship extends BaseResource {
  resource_type: "relationship";
  from: string;
  to: string;
  from_columns: string[];
  to_columns: string[];
}

// Metric resource
export interface Metric extends BaseResource {
  resource_type: "metric";
  expression: string;
}

// Code resource
export interface Code {
  name: string;
  path: string;
  code: string;
  type: CodeType;
}

// Full manifest
export interface Manifest {
  sources: Record<string, Source>;
  models: Record<string, Model>;
  relationships: Record<string, Relationship>;
  metrics: Record<string, Metric>;
  code: Record<string, Code>;
}

// API Response types
export interface SourcesResponse {
  sources: Source[];
  count: number;
}

export interface ModelsResponse {
  models: Model[];
  count: number;
}

export interface RelationshipsResponse {
  relationships: Relationship[];
  count: number;
}

export interface MetricsResponse {
  metrics: Metric[];
  count: number;
}

// Graph types for React Flow
export interface GraphNode {
  id: string;
  type: "source" | "model";
  data: {
    label: string;
    resourceType: ResourceType;
    description?: string;
    tags: string[];
    columnCount: number;
    modelType?: ModelType;
    schedule?: string;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: "dependency" | "relationship";
  data?: {
    name?: string;
    fromColumns?: string[];
    toColumns?: string[];
  };
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  nodeCount: number;
  edgeCount: number;
}

// Search types
export interface SearchResult {
  name: string;
  resourceType: ResourceType;
  modelType?: ModelType;
  description?: string;
  tags: string[];
}

export interface SearchResponse {
  results: SearchResult[];
  count: number;
  query: string;
}

// Stats types
export interface ManifestStats {
  sources: number;
  models: number;
  relationships: number;
  metrics: number;
  modelTypes: Record<string, number>;
  scheduledModels: number;
  totalSourceColumns: number;
  totalModelColumns: number;
  totalColumns: number;
  uniqueTags: string[];
  tagCount: number;
}

// Health check
export interface HealthResponse {
  status: "healthy" | "unhealthy";
  service: string;
}
