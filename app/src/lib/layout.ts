import { Node, Edge } from "reactflow";

export type LayoutNode = Node & {
  position: { x: number; y: number };
};

export type LayoutEdge = Edge & {
  sourcePosition?: "top" | "right" | "bottom" | "left";
  targetPosition?: "top" | "right" | "bottom" | "left";
};

export function layout(
  nodes: Node[],
  edges: Edge[],
  direction: "TB" | "LR" = "LR"
): { nodes: LayoutNode[]; edges: LayoutEdge[] } {
  // Simple grid layout for now
  const cols = Math.ceil(Math.sqrt(nodes.length));
  const layoutNodes: LayoutNode[] = nodes.map((node, index) => ({
    ...node,
    position: {
      x: (index % cols) * 200 + 100,
      y: Math.floor(index / cols) * 150 + 100,
    },
  }));

  // Simple edge positioning
  const layoutEdges: LayoutEdge[] = edges.map((edge) => ({
    ...edge,
    sourcePosition: "right" as const,
    targetPosition: "left" as const,
  }));

  return { nodes: layoutNodes, edges: layoutEdges };
}
