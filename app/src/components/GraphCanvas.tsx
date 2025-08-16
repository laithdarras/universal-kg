import React, { useCallback, useMemo } from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
} from "reactflow";
import "reactflow/dist/style.css";
import { GraphData, GraphNode } from "../lib/api";

interface GraphCanvasProps {
  graphData: GraphData | null;
  selectedNode: GraphNode | null;
  onNodeClick: (node: GraphNode) => void;
  citedNodes: string[];
  citedEdges: string[];
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({
  graphData,
  selectedNode,
  onNodeClick,
  citedNodes,
  citedEdges,
}) => {
  const nodes = useMemo(() => {
    console.log("DEBUG: GraphCanvas - graphData received:", graphData);
    console.log(
      "DEBUG: GraphCanvas - nodes count:",
      graphData?.nodes?.length || 0
    );
    if (!graphData) return [];

    return graphData.nodes.map((node) => ({
      id: node.id,
      position: { x: Math.random() * 800, y: Math.random() * 600 },
      data: {
        label: node.label,
        isCited: citedNodes.includes(node.id),
      },
      style: {
        background: citedNodes.includes(node.id) ? "#3b82f6" : "#374151",
        color: "white",
        border: citedNodes.includes(node.id)
          ? "3px solid #fbbf24"
          : "1px solid #6b7280",
        borderRadius: "8px",
        padding: "8px 12px",
        fontSize: "12px",
        fontWeight: citedNodes.includes(node.id) ? "bold" : "normal",
      },
    }));
  }, [graphData, citedNodes]);

  const edges = useMemo(() => {
    console.log(
      "DEBUG: GraphCanvas - edges count:",
      graphData?.edges?.length || 0
    );
    if (!graphData) return [];

    return graphData.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.relation,
      style: {
        stroke: citedEdges.includes(edge.id) ? "#ef4444" : "#6b7280",
        strokeWidth: citedEdges.includes(edge.id) ? 3 : 1,
      },
      labelStyle: {
        fill: citedEdges.includes(edge.id) ? "#ef4444" : "#9ca3af",
        fontSize: "10px",
        fontWeight: citedEdges.includes(edge.id) ? "bold" : "normal",
      },
    }));
  }, [graphData, citedEdges]);

  const [nodesState, setNodes, onNodesChange] = useNodesState(nodes);
  const [edgesState, setEdges, onEdgesChange] = useEdgesState(edges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClickHandler = useCallback(
    (event: React.MouseEvent, node: Node) => {
      const graphNode = graphData?.nodes.find((n) => n.id === node.id);
      if (graphNode) {
        onNodeClick(graphNode);
      }
    },
    [graphData, onNodeClick]
  );

  // Update nodes and edges when graphData changes
  React.useEffect(() => {
    console.log("DEBUG: GraphCanvas - setting nodes:", nodes.length);
    console.log("DEBUG: GraphCanvas - setting edges:", edges.length);
    setNodes(nodes);
    setEdges(edges);
  }, [nodes, edges, setNodes, setEdges]);

  if (!graphData) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900">
        <div className="text-gray-400 text-center">
          <p className="text-lg mb-2">No Graph Data</p>
          <p className="text-sm">Upload URLs to build a knowledge graph</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-900">
      <ReactFlow
        nodes={nodesState}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClickHandler}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <Background color="#374151" gap={16} />
      </ReactFlow>
    </div>
  );
};
