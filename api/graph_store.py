import networkx as nx
import uuid
from typing import Dict, List, Any, Set, Tuple
import re
from collections import defaultdict

class GraphStore:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.node_id_map = {}  # (label, type) -> node_id
        self.edge_id_map = {}  # (subject_id, object_id, relation) -> edge_id

    def upsert_triple(self, subject: str, relation: str, object_val: str, source_id: str, confidence: float = 0.0):
        """
        Add or update a triple in the graph.
        Creates nodes for subject and object if they don't exist.
        """
        print(f"DEBUG: upsert_triple called with: {subject} --{relation}--> {object_val}")
        
        # Get or create node IDs
        subject_id = self._get_or_create_node_id(subject, "entity")
        object_id = self._get_or_create_node_id(object_val, "entity")
        
        # Create edge key for deduplication
        edge_key = (subject_id, object_id, relation)
        
        # Check if edge already exists
        if edge_key in self.edge_id_map:
            # Update existing edge with additional source and keep max confidence
            edge_id = self.edge_id_map[edge_key]
            if "sources" not in self.graph.edges[subject_id, object_id, edge_id]:
                self.graph.edges[subject_id, object_id, edge_id]["sources"] = []
            self.graph.edges[subject_id, object_id, edge_id]["sources"].append(source_id)
            
            # Keep the maximum confidence
            existing_confidence = self.graph.edges[subject_id, object_id, edge_id].get("confidence", 0.0)
            self.graph.edges[subject_id, object_id, edge_id]["confidence"] = max(existing_confidence, confidence)
            print(f"DEBUG: Updated existing edge {edge_id}")
        else:
            # Create new edge
            edge_id = str(uuid.uuid4())
            self.edge_id_map[edge_key] = edge_id
            self.graph.add_edge(
                subject_id, 
                object_id, 
                key=edge_id,
                relation=relation,
                sources=[source_id],
                confidence=confidence
            )
            print(f"DEBUG: Created new edge {edge_id}")
        
        print(f"DEBUG: Graph now has {len(self.graph.nodes())} nodes and {len(self.graph.edges())} edges")
    
    def _get_or_create_node_id(self, label: str, node_type: str) -> str:
        """Get existing node ID or create new node."""
        node_key = (label, node_type)
        
        if node_key in self.node_id_map:
            return self.node_id_map[node_key]
        
        # Create new node
        node_id = str(uuid.uuid4())
        self.node_id_map[node_key] = node_id
        self.graph.add_node(node_id, label=label, type=node_type)
        return node_id
    
    def to_dto(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert graph to DTO format for JSON serialization."""
        nodes = []
        edges = []
        
        print(f"DEBUG: to_dto() - Graph has {len(self.graph.nodes())} nodes and {len(self.graph.edges())} edges")
        
        # Convert nodes
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": attrs.get("label", ""),
                "type": attrs.get("type", "entity")
            })
        
        # Convert edges
        for source, target, edge_id, attrs in self.graph.edges(data=True, keys=True):
            edges.append({
                "id": edge_id,
                "source": source,
                "target": target,
                "relation": attrs.get("relation", ""),
                "sources": attrs.get("sources", [])
            })
        
        result = {"nodes": nodes, "edges": edges}
        print(f"DEBUG: to_dto() - Returning {len(nodes)} nodes and {len(edges)} edges")
        return result

    def get_subgraph_by_keywords(self, keywords: List[str]) -> 'GraphStore':
        """Get subgraph containing nodes and edges related to keywords."""
        if not self.graph.nodes():
            return GraphStore()  # Return empty graph if no nodes exist
        
        # Find nodes that contain any of the keywords
        relevant_nodes = set()
        for node_id, attrs in self.graph.nodes(data=True):
            label = attrs.get("label", "").lower()
            for keyword in keywords:
                if keyword.lower() in label:
                    relevant_nodes.add(node_id)
                    break
        
        # If no relevant nodes found, return a small sample of the graph
        if not relevant_nodes:
            all_nodes = list(self.graph.nodes())
            relevant_nodes = set(all_nodes[:10])  # Take first 10 nodes
        
        # Get edges between relevant nodes
        relevant_edges = set()
        for source, target, edge_id in self.graph.edges(keys=True):
            if source in relevant_nodes and target in relevant_nodes:
                relevant_edges.add((source, target, edge_id))
        
        # Create subgraph
        subgraph_store = GraphStore()
        subgraph_store.graph = self.graph.subgraph(relevant_nodes).copy()
        
        # Add the relevant edges
        for source, target, edge_id in relevant_edges:
            edge_data = self.graph.edges[source, target, edge_id].copy()
            subgraph_store.graph.add_edge(source, target, key=edge_id, **edge_data)
        
        return subgraph_store

# Global graph store instance
graph_store = GraphStore()
