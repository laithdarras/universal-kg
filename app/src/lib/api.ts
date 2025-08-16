export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  sources: string[];
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface QAResponse {
  answer: string;
  cited_nodes: string[];
  cited_edges: string[];
}

const API_BASE = "/api";

export const api = {
  async ingest(urls: string[]): Promise<GraphData> {
    console.log("DEBUG: Making ingest request with URLs:", urls);
    const response = await fetch(`${API_BASE}/ingest`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ urls }),
    });

    console.log("DEBUG: Ingest response status:", response.status);
    if (!response.ok) {
      throw new Error(`Ingest failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("DEBUG: Ingest response data:", data);
    return data;
  },

  async ingestFile(file: File): Promise<GraphData> {
    console.log("DEBUG: Making ingestFile request with file:", file.name);
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/ingest-file`, {
      method: "POST",
      body: formData,
    });

    console.log("DEBUG: IngestFile response status:", response.status);
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`File ingest failed: ${errorText}`);
    }

    const data = await response.json();
    console.log("DEBUG: IngestFile response data:", data);
    return data;
  },

  async getGraph(): Promise<GraphData> {
    console.log("DEBUG: Making getGraph request");
    const response = await fetch(`${API_BASE}/graph`);

    console.log("DEBUG: GetGraph response status:", response.status);
    if (!response.ok) {
      throw new Error(`Failed to get graph: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("DEBUG: GetGraph response data:", data);
    return data;
  },

  async qa(question: string): Promise<QAResponse> {
    const response = await fetch(`${API_BASE}/qa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`QA failed: ${response.statusText}`);
    }

    return response.json();
  },
};
