import React, { useState, useEffect } from "react";
import { UploadPanel } from "./components/UploadPanel";
import { QAPanel } from "./components/QAPanel";
import { GraphCanvas } from "./components/GraphCanvas";
import { NodeDetails } from "./components/NodeDetails";
import { api, GraphData, GraphNode } from "./lib/api";

function App() {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [citedNodes, setCitedNodes] = useState<string[]>([]);
  const [citedEdges, setCitedEdges] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load initial graph data
  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    setIsLoading(true);
    try {
      const data = await api.getGraph();
      console.log("DEBUG: App - received graph data:", data);
      console.log("DEBUG: App - nodes count:", data?.nodes?.length || 0);
      console.log("DEBUG: App - edges count:", data?.edges?.length || 0);
      setGraphData(data);
    } catch (error) {
      console.error("Failed to load graph data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGraphBuilt = () => {
    loadGraphData();
  };

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  const handleAnswerReceived = (citedNodes: string[], citedEdges: string[]) => {
    setCitedNodes(citedNodes);
    setCitedEdges(citedEdges);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="h-screen flex">
        {/* Left Panel - Upload & QA */}
        <div className="w-80 bg-gray-800 p-4 space-y-4 overflow-y-auto">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-white">Universal KG</h1>
            <p className="text-gray-400 text-sm">Knowledge Graph Explorer</p>
          </div>

          <UploadPanel onGraphBuilt={handleGraphBuilt} />
          <QAPanel onAnswerReceived={handleAnswerReceived} />
        </div>

        {/* Center Panel - Graph Canvas */}
        <div className="flex-1 relative">
          {isLoading ? (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-400">Loading graph...</p>
              </div>
            </div>
          ) : (
            <GraphCanvas
              graphData={graphData}
              selectedNode={selectedNode}
              onNodeClick={handleNodeClick}
              citedNodes={citedNodes}
              citedEdges={citedEdges}
            />
          )}
        </div>

        {/* Right Panel - Node Details */}
        <div className="w-80 bg-gray-800 p-4 overflow-y-auto">
          <NodeDetails node={selectedNode} graphData={graphData} />
        </div>
      </div>
    </div>
  );
}

export default App;
