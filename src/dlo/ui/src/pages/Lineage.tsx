import { useCallback, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  type Node,
  type Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { Header } from '@/components/layout';
import { nodeTypes } from '@/components/lineage';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useManifest } from '@/context';

// Simple layout algorithm
function getLayoutedElements(
  nodes: Node[],
  edges: Edge[],
) {
  const nodeWidth = 180;
  const nodeHeight = 70;
  const horizontalSpacing = 250;
  const verticalSpacing = 100;

  // Build adjacency list
  const adjacency: Record<string, string[]> = {};
  const inDegree: Record<string, number> = {};
  
  nodes.forEach((node) => {
    adjacency[node.id] = [];
    inDegree[node.id] = 0;
  });

  edges.forEach((edge) => {
    if (adjacency[edge.source]) {
      adjacency[edge.source].push(edge.target);
    }
    if (inDegree[edge.target] !== undefined) {
      inDegree[edge.target]++;
    }
  });

  // Topological sort with levels
  const levels: string[][] = [];
  const visited = new Set<string>();
  const queue: string[] = [];

  Object.keys(inDegree).forEach((nodeId) => {
    if (inDegree[nodeId] === 0) {
      queue.push(nodeId);
    }
  });

  while (queue.length > 0) {
    const levelNodes = [...queue];
    queue.length = 0;
    levels.push(levelNodes);

    levelNodes.forEach((nodeId) => {
      visited.add(nodeId);
      adjacency[nodeId]?.forEach((neighbor) => {
        inDegree[neighbor]--;
        if (inDegree[neighbor] === 0 && !visited.has(neighbor)) {
          queue.push(neighbor);
        }
      });
    });
  }

  const unvisited = nodes.filter((n) => !visited.has(n.id)).map((n) => n.id);
  if (unvisited.length > 0) {
    levels.push(unvisited);
  }

  const positionedNodes = nodes.map((node) => {
    const levelIndex = levels.findIndex((level) => level.includes(node.id));
    const levelNodes = levels[levelIndex] || [];
    const indexInLevel = levelNodes.indexOf(node.id);

    const x = levelIndex * horizontalSpacing;
    const y = indexInLevel * verticalSpacing - (levelNodes.length * verticalSpacing) / 2 + 200;

    return {
      ...node,
      position: { x, y },
      style: { width: nodeWidth, height: nodeHeight },
    };
  });

  return { nodes: positionedNodes, edges };
}

export function Lineage() {
  const navigate = useNavigate();
  const { graph, isLoading, error, refetch } = useManifest();

  const { layoutedNodes, layoutedEdges } = useMemo(() => {
    if (!graph.nodes.length) {
      return { layoutedNodes: [], layoutedEdges: [] };
    }

    const nodes: Node[] = graph.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: { x: 0, y: 0 },
      data: node.data,
    }));

    const edges: Edge[] = graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: edge.type === 'dependency',
      style: {
        stroke: edge.type === 'relationship' ? 'hsl(280, 70%, 50%)' : 'hsl(330, 81%, 60%)',
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: edge.type === 'relationship' ? 'hsl(280, 70%, 50%)' : 'hsl(330, 81%, 60%)',
      },
    }));

    const layouted = getLayoutedElements(nodes, edges);
    return { layoutedNodes: layouted.nodes, layoutedEdges: layouted.edges };
  }, [graph]);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    if (layoutedNodes.length > 0) {
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    }
  }, [layoutedNodes, layoutedEdges, setNodes, setEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const data = node.data as { resourceType?: string };
      const resourceType = data.resourceType;
      if (resourceType === 'source') {
        navigate(`/sources/${node.id}`);
      } else if (resourceType === 'model') {
        navigate(`/models/${node.id}`);
      }
    },
    [navigate]
  );

  if (isLoading) {
    return (
      <div className="flex flex-col h-full">
        <Header title="Lineage Graph" description="Data lineage visualization" />
        <div className="flex-1 p-6">
          <Skeleton className="w-full h-full min-h-[500px]" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full">
        <Header title="Lineage Graph" description="Data lineage visualization" />
        <div className="flex-1 flex items-center justify-center p-6">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive">Error Loading Graph</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {error.message}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Lineage Graph"
        description={`${graph.nodes.length} nodes, ${graph.edges.length} edges`}
        onRefresh={() => refetch()}
        isLoading={isLoading}
      />

      <div className="flex-1 p-6">
        <Card className="h-full min-h-[600px]">
          <CardContent className="p-0 h-full">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
              fitViewOptions={{ padding: 0.2 }}
              minZoom={0.1}
              maxZoom={2}
              defaultEdgeOptions={{
                type: 'smoothstep',
              }}
            >
              <Controls className="!bg-card !border-border !shadow-md" />
              <MiniMap
                nodeColor={(node) => {
                  if (node.type === 'source') return 'hsl(210, 70%, 50%)';
                  const data = node.data as { modelType?: string };
                  const modelType = data?.modelType;
                  if (modelType === 'materialized') return 'hsl(150, 70%, 40%)';
                  if (modelType === 'view') return 'hsl(40, 70%, 50%)';
                  return 'hsl(220, 10%, 50%)';
                }}
                className="!bg-card !border-border"
              />
              <Background
                variant={BackgroundVariant.Dots}
                gap={20}
                size={1}
                color="hsl(var(--muted-foreground) / 0.2)"
              />
            </ReactFlow>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
