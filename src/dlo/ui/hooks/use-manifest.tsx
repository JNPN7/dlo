"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchManifest } from "@/lib/api/manifest";
import type {
  Manifest,
  Source,
  Model,
  Relationship,
  Metric,
  ModelType,
} from "@/types/manifest";

// Stats type
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

// Graph types for React Flow
export interface GraphNode {
  id: string;
  type: "source" | "model";
  data: {
    label: string;
    resourceType: "source" | "model";
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

// Search result type
export interface SearchResult {
  name: string;
  resourceType: "source" | "model" | "relationship" | "metric";
  modelType?: ModelType;
  description?: string;
  tags: string[];
}

// Context value type
interface ManifestContextValue {
  // Raw data
  manifest: Manifest | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;

  // Derived data as arrays
  sources: Source[];
  models: Model[];
  relationships: Relationship[];
  metrics: Metric[];

  // Getters for individual resources
  getSource: (name: string) => Source | undefined;
  getModel: (name: string) => Model | undefined;
  getRelationship: (name: string) => Relationship | undefined;
  getMetric: (name: string) => Metric | undefined;

  // Computed data
  stats: ManifestStats;
  graph: { nodes: GraphNode[]; edges: GraphEdge[] };

  // Search function
  search: (query: string, resourceType?: string) => SearchResult[];
}

const ManifestContext = createContext<ManifestContextValue | null>(null);

// Compute stats from manifest
function computeStats(manifest: Manifest | null): ManifestStats {
  if (!manifest) {
    return {
      sources: 0,
      models: 0,
      relationships: 0,
      metrics: 0,
      modelTypes: {},
      scheduledModels: 0,
      totalSourceColumns: 0,
      totalModelColumns: 0,
      totalColumns: 0,
      uniqueTags: [],
      tagCount: 0,
    };
  }

  const sources = Object.values(manifest.sources);
  const models = Object.values(manifest.models);
  const relationships = Object.values(manifest.relationships);
  const metrics = Object.values(manifest.metrics);

  // Count model types
  const modelTypes: Record<string, number> = {};
  let scheduledModels = 0;
  for (const model of models) {
    const modelType = model.type || "unknown";
    modelTypes[modelType] = (modelTypes[modelType] || 0) + 1;
    if (model.schedule) {
      scheduledModels++;
    }
  }

  // Count columns
  const totalSourceColumns = sources.reduce((sum, s) => sum + s.columns.length, 0);
  const totalModelColumns = models.reduce((sum, m) => sum + m.columns.length, 0);

  // Collect unique tags
  const allTags = new Set<string>();
  for (const source of sources) {
    source.tags?.forEach((tag) => allTags.add(tag));
  }
  for (const model of models) {
    model.tags?.forEach((tag) => allTags.add(tag));
  }
  for (const rel of relationships) {
    rel.tags?.forEach((tag) => allTags.add(tag));
  }
  for (const metric of metrics) {
    metric.tags?.forEach((tag) => allTags.add(tag));
  }

  return {
    sources: sources.length,
    models: models.length,
    relationships: relationships.length,
    metrics: metrics.length,
    modelTypes,
    scheduledModels,
    totalSourceColumns,
    totalModelColumns,
    totalColumns: totalSourceColumns + totalModelColumns,
    uniqueTags: Array.from(allTags).sort(),
    tagCount: allTags.size,
  };
}

// Compute graph data from manifest
function computeGraph(manifest: Manifest | null): { nodes: GraphNode[]; edges: GraphEdge[] } {
  if (!manifest) {
    return { nodes: [], edges: [] };
  }

  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const nodeIds = new Set<string>();

  // Add source nodes
  for (const [name, source] of Object.entries(manifest.sources)) {
    nodeIds.add(name);
    nodes.push({
      id: name,
      type: "source",
      data: {
        label: name,
        resourceType: "source",
        description: source.description,
        tags: source.tags || [],
        columnCount: source.columns.length,
      },
    });
  }

  // Add model nodes
  for (const [name, model] of Object.entries(manifest.models)) {
    nodeIds.add(name);
    nodes.push({
      id: name,
      type: "model",
      data: {
        label: name,
        resourceType: "model",
        modelType: model.type,
        description: model.description,
        tags: model.tags || [],
        columnCount: model.columns.length,
        schedule: model.schedule,
      },
    });

    // Add edges from dependencies
    if (model.depends_on?.nodes) {
      for (const dep of model.depends_on.nodes) {
        if (nodeIds.has(dep) || manifest.sources[dep] || manifest.models[dep]) {
          edges.push({
            id: `${dep}-${name}`,
            source: dep,
            target: name,
            type: "dependency",
          });
        }
      }
    }
  }

  // Add relationship edges
  for (const [name, rel] of Object.entries(manifest.relationships)) {
    const fromNode = rel.from;
    const toNode = rel.to;
    if (nodeIds.has(fromNode) && nodeIds.has(toNode)) {
      edges.push({
        id: `rel-${name}`,
        source: fromNode,
        target: toNode,
        type: "relationship",
        data: {
          name,
          fromColumns: rel.from_columns,
          toColumns: rel.to_columns,
        },
      });
    }
  }

  return { nodes, edges };
}

// Search function
function createSearchFn(manifest: Manifest | null) {
  return (query: string, resourceType?: string): SearchResult[] => {
    if (!manifest || !query) {
      return [];
    }

    const q = query.toLowerCase();
    const results: SearchResult[] = [];

    const matches = (resource: { name: string; description?: string; tags?: string[] }) => {
      const nameMatch = resource.name.toLowerCase().includes(q);
      const descMatch = resource.description?.toLowerCase().includes(q);
      const tagMatch = resource.tags?.some((tag) => tag.toLowerCase().includes(q));
      return nameMatch || descMatch || tagMatch;
    };

    // Search sources
    if (!resourceType || resourceType === "source") {
      for (const [name, source] of Object.entries(manifest.sources)) {
        if (matches(source)) {
          results.push({
            name,
            resourceType: "source",
            description: source.description,
            tags: source.tags || [],
          });
        }
      }
    }

    // Search models
    if (!resourceType || resourceType === "model") {
      for (const [name, model] of Object.entries(manifest.models)) {
        if (matches(model)) {
          results.push({
            name,
            resourceType: "model",
            modelType: model.type,
            description: model.description,
            tags: model.tags || [],
          });
        }
      }
    }

    // Search relationships
    if (!resourceType || resourceType === "relationship") {
      for (const [name, rel] of Object.entries(manifest.relationships)) {
        if (matches(rel)) {
          results.push({
            name,
            resourceType: "relationship",
            description: rel.description,
            tags: rel.tags || [],
          });
        }
      }
    }

    // Search metrics
    if (!resourceType || resourceType === "metric") {
      for (const [name, metric] of Object.entries(manifest.metrics)) {
        if (matches(metric)) {
          results.push({
            name,
            resourceType: "metric",
            description: metric.description,
            tags: metric.tags || [],
          });
        }
      }
    }

    return results;
  };
}

// Provider component
export function ManifestProvider({ children }: { children: ReactNode }) {
  const {
    data: manifest,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["manifest"],
    queryFn: () => fetchManifest(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const value = useMemo<ManifestContextValue>(() => {
    const sources = manifest ? Object.values(manifest.sources) : [];
    const models = manifest ? Object.values(manifest.models) : [];
    const relationships = manifest ? Object.values(manifest.relationships) : [];
    const metrics = manifest ? Object.values(manifest.metrics) : [];

    return {
      manifest: manifest ?? null,
      isLoading,
      error: error as Error | null,
      refetch,

      sources,
      models,
      relationships,
      metrics,

      getSource: (name: string) => manifest?.sources[name],
      getModel: (name: string) => manifest?.models[name],
      getRelationship: (name: string) => manifest?.relationships[name],
      getMetric: (name: string) => manifest?.metrics[name],

      stats: computeStats(manifest ?? null),
      graph: computeGraph(manifest ?? null),
      search: createSearchFn(manifest ?? null),
    };
  }, [manifest, isLoading, error, refetch]);

  return <ManifestContext.Provider value={value}>{children}</ManifestContext.Provider>;
}

// Hook to use manifest context
export function useManifest() {
  const context = useContext(ManifestContext);
  if (!context) {
    throw new Error("useManifest must be used within a ManifestProvider");
  }
  return context;
}
