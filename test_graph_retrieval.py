import unittest
from api.graph_store import GraphStore
import networkx as nx

class TestGraphRetrieval(unittest.TestCase):
    
    def setUp(self):
        """Set up a test graph for each test."""
        self.graph_store = GraphStore()
        
        # Create a simple test graph
        # AI -> Machine Learning -> Neural Networks
        # AI -> Natural Language Processing -> Text
        # AI -> Computer Vision -> Images
        # Machine Learning -> Deep Learning
        # Neural Networks -> Deep Learning
        
        test_triples = [
            ("AI", "includes", "Machine Learning", "source1"),
            ("AI", "includes", "Natural Language Processing", "source1"),
            ("AI", "includes", "Computer Vision", "source1"),
            ("Machine Learning", "includes", "Neural Networks", "source1"),
            ("Machine Learning", "includes", "Deep Learning", "source1"),
            ("Neural Networks", "enables", "Deep Learning", "source1"),
            ("Natural Language Processing", "processes", "Text", "source1"),
            ("Computer Vision", "processes", "Images", "source1"),
            ("Deep Learning", "uses", "Neural Networks", "source1"),
            ("Text", "contains", "Language", "source1"),
            ("Images", "contains", "Visual Data", "source1"),
        ]
        
        for subject, relation, obj, source in test_triples:
            self.graph_store.upsert_triple(subject, relation, obj, source)
    
    def test_simple_case_two_related_nodes(self):
        """Test case with two related nodes: question mentions both → path included."""
        # Question mentions both "AI" and "Machine Learning"
        keywords = ["ai", "machine", "learning"]
        
        subgraph = self.graph_store.get_subgraph_by_keywords(keywords)
        
        # Should include AI and Machine Learning nodes
        node_labels = [attrs.get("label", "") for _, attrs in subgraph.graph.nodes(data=True)]
        self.assertIn("AI", node_labels)
        self.assertIn("Machine Learning", node_labels)
        
        # Should include the path between them
        edge_relations = [attrs.get("relation", "") for _, _, _, attrs in subgraph.graph.edges(data=True, keys=True)]
        self.assertIn("includes", edge_relations)
        
        # Should include some 2-hop neighbors
        self.assertIn("Neural Networks", node_labels)
        self.assertIn("Deep Learning", node_labels)
    
    def test_single_entity_detection(self):
        """Test case with only one detected entity: returns 2-hop expansion."""
        # Question mentions only "Neural Networks"
        keywords = ["neural", "networks"]
        
        subgraph = self.graph_store.get_subgraph_by_keywords(keywords)
        
        # Should include Neural Networks
        node_labels = [attrs.get("label", "") for _, attrs in subgraph.graph.nodes(data=True)]
        self.assertIn("Neural Networks", node_labels)
        
        # Should include 1-hop neighbors
        self.assertIn("Machine Learning", node_labels)  # parent
        self.assertIn("Deep Learning", node_labels)     # child
        
        # Should include 2-hop neighbors
        self.assertIn("AI", node_labels)  # grandparent
        self.assertIn("AI", node_labels)  # through Machine Learning
    
    def test_no_entity_detected_fallback(self):
        """Test case with no entity detected: returns fallback neutral subgraph."""
        # Question with no relevant keywords
        keywords = ["xyz", "unknown", "term"]
        
        subgraph = self.graph_store.get_subgraph_by_keywords(keywords)
        
        # Should return a subgraph (not empty)
        self.assertGreater(len(subgraph.graph.nodes()), 0)
        
        # Should be capped to reasonable size
        self.assertLessEqual(len(subgraph.graph.nodes()), 25)
        self.assertLessEqual(len(subgraph.graph.edges()), 40)
    
    def test_alias_expansion(self):
        """Test that alias expansion works correctly."""
        # Question uses "ml" which should expand to "machine learning"
        keywords = ["ml"]
        
        subgraph = self.graph_store.get_subgraph_by_keywords(keywords)
        
        # Should find Machine Learning through alias expansion
        node_labels = [attrs.get("label", "") for _, attrs in subgraph.graph.nodes(data=True)]
        self.assertIn("Machine Learning", node_labels)
    
    def test_size_capping(self):
        """Test that subgraph sizes are properly capped."""
        # Create a larger graph for testing
        large_graph = GraphStore()
        
        # Add many nodes and edges
        for i in range(50):
            large_graph.upsert_triple(f"Node{i}", "connects", f"Node{i+1}", "source")
        
        # Query that would match many nodes
        keywords = ["node"]
        
        subgraph = large_graph.get_subgraph_by_keywords(keywords)
        
        # Should be capped
        self.assertLessEqual(len(subgraph.graph.nodes()), 25)
        self.assertLessEqual(len(subgraph.graph.edges()), 40)
    
    def test_shortest_paths(self):
        """Test that shortest paths between hit nodes are included."""
        # Question mentions "AI" and "Deep Learning" (which are connected via path)
        keywords = ["ai", "deep", "learning"]
        
        subgraph = self.graph_store.get_subgraph_by_keywords(keywords)
        
        # Should include both nodes
        node_labels = [attrs.get("label", "") for _, attrs in subgraph.graph.nodes(data=True)]
        self.assertIn("AI", node_labels)
        self.assertIn("Deep Learning", node_labels)
        
        # Should include the path between them
        edge_relations = [attrs.get("relation", "") for _, _, _, attrs in subgraph.graph.edges(data=True, keys=True)]
        self.assertIn("includes", edge_relations)  # AI -> Machine Learning
        self.assertIn("includes", edge_relations)  # Machine Learning -> Deep Learning
    
    def test_edge_detection(self):
        """Test that edges matching query terms are included."""
        # Question mentions "includes" relation
        keywords = ["includes"]
        
        subgraph = self.graph_store.get_subgraph_by_keywords(keywords)
        
        # Should include edges with "includes" relation
        edge_relations = [attrs.get("relation", "") for _, _, _, attrs in subgraph.graph.edges(data=True, keys=True)]
        self.assertIn("includes", edge_relations)
        
        # Should include the endpoints of those edges
        node_labels = [attrs.get("label", "") for _, attrs in subgraph.graph.nodes(data=True)]
        self.assertIn("AI", node_labels)
        self.assertIn("Machine Learning", node_labels)
    
    def test_empty_graph(self):
        """Test handling of empty graph."""
        empty_graph = GraphStore()
        
        subgraph = empty_graph.get_subgraph_by_keywords(["test"])
        
        # Should return empty graph
        self.assertEqual(len(subgraph.graph.nodes()), 0)
        self.assertEqual(len(subgraph.graph.edges()), 0)
    
    def test_deterministic_capping(self):
        """Test that capping is deterministic (same result for same input)."""
        # Create a graph with many nodes
        test_graph = GraphStore()
        for i in range(30):
            test_graph.upsert_triple(f"Node{i}", "connects", f"Node{i+1}", "source")
        
        # Query multiple times
        keywords = ["node"]
        subgraph1 = test_graph.get_subgraph_by_keywords(keywords)
        subgraph2 = test_graph.get_subgraph_by_keywords(keywords)
        
        # Should be identical
        self.assertEqual(len(subgraph1.graph.nodes()), len(subgraph2.graph.nodes()))
        self.assertEqual(len(subgraph1.graph.edges()), len(subgraph2.graph.edges()))

if __name__ == "__main__":
    unittest.main()
