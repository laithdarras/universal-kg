import React from "react";
import { GraphNode, GraphEdge } from "../lib/api";

interface NodeDetailsProps {
  node: GraphNode | null;
  graphData: { nodes: GraphNode[]; edges: GraphEdge[] } | null;
}

export const NodeDetails: React.FC<NodeDetailsProps> = ({
  node,
  graphData,
}) => {
  if (!node) {
    return (
      <div className="bg-gray-800 p-4 rounded-lg">
        <h2 className="text-xl font-bold text-white mb-4">Node Details</h2>
        <div className="text-gray-400 text-sm">
          Click on a node to view its details
        </div>
      </div>
    );
  }

  // Find connected edges
  const connectedEdges =
    graphData?.edges.filter(
      (edge) => edge.source === node.id || edge.target === node.id
    ) || [];

  // Find connected nodes
  const connectedNodeIds = new Set<string>();
  connectedEdges.forEach((edge) => {
    if (edge.source === node.id) connectedNodeIds.add(edge.target);
    if (edge.target === node.id) connectedNodeIds.add(edge.source);
  });

  const connectedNodes =
    graphData?.nodes.filter((n) => connectedNodeIds.has(n.id)) || [];

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h2 className="text-xl font-bold text-white mb-4">Node Details</h2>

      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">Label</h3>
          <p className="text-white text-lg font-semibold">{node.label}</p>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">Type</h3>
          <p className="text-white">{node.type}</p>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-300 mb-1">ID</h3>
          <p className="text-gray-400 text-xs font-mono break-all">{node.id}</p>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-300 mb-2">
            Connected Nodes ({connectedNodes.length})
          </h3>
          <div className="space-y-1">
            {connectedNodes.map((connectedNode) => (
              <div
                key={connectedNode.id}
                className="bg-gray-700 p-2 rounded text-sm"
              >
                <span className="text-white">{connectedNode.label}</span>
                <span className="text-gray-400 text-xs block">
                  {connectedNode.type}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-300 mb-2">
            Connections ({connectedEdges.length})
          </h3>
          <div className="space-y-1">
            {connectedEdges.map((edge) => {
              const isSource = edge.source === node.id;
              const connectedNode = graphData?.nodes.find(
                (n) => n.id === (isSource ? edge.target : edge.source)
              );

              return (
                <div key={edge.id} className="bg-gray-700 p-2 rounded text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-white">
                      {isSource ? "→" : "←"} {connectedNode?.label}
                    </span>
                    <span className="text-blue-400 text-xs">
                      {edge.relation}
                    </span>
                  </div>
                  {edge.sources.length > 0 && (
                    <div className="text-gray-400 text-xs mt-1">
                      Sources: {edge.sources.length}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
