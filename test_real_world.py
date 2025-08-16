#!/usr/bin/env python3
"""
Test script to verify triple quality improvements with real-world data.
Tests the API endpoints with sample URLs to see the quality improvements in action.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is running."""
    print("=== Testing API Health ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ API is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to API: {e}")
        return False

def test_ingest_sample_urls():
    """Test ingesting sample URLs to see triple quality improvements."""
    print("\n=== Testing Triple Quality with Real URLs ===")
    
    # Sample URLs that should produce meaningful triples
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning"
    ]
    
    # For testing, let's use a smaller subset to avoid overwhelming the system
    test_urls = test_urls[:1]  # Start with just one URL
    
    print(f"Testing with URLs: {test_urls}")
    
    try:
        # Ingest the URLs
        response = requests.post(
            f"{BASE_URL}/api/ingest",
            json={"urls": test_urls},
            timeout=60  # Longer timeout for processing
        )
        
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            
            print(f"✓ Successfully ingested data")
            print(f"Nodes: {len(nodes)}")
            print(f"Edges: {len(edges)}")
            
            # Analyze the quality of extracted triples
            analyze_triple_quality(nodes, edges)
            
            return data
        else:
            print(f"✗ Ingest failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error during ingest: {e}")
        return None

def analyze_triple_quality(nodes, edges):
    """Analyze the quality of extracted triples."""
    print("\n=== Triple Quality Analysis ===")
    
    # Check for junk nodes
    junk_indicators = ["an", "the", "a", "there", "what", "not", "issue", "thing", "something", "anything", "everything"]
    junk_nodes = []
    valid_nodes = []
    
    for node in nodes:
        label = node.get("label", "").lower()
        is_junk = any(indicator in label for indicator in junk_indicators)
        if is_junk:
            junk_nodes.append(node["label"])
        else:
            valid_nodes.append(node["label"])
    
    print(f"Valid nodes: {len(valid_nodes)}")
    print(f"Junk nodes: {len(junk_nodes)}")
    
    if junk_nodes:
        print(f"Junk nodes found: {junk_nodes[:5]}")  # Show first 5
    else:
        print("✓ No junk nodes detected!")
    
    # Check relation quality
    relation_counts = {}
    for edge in edges:
        relation = edge.get("relation", "")
        relation_counts[relation] = relation_counts.get(relation, 0) + 1
    
    print(f"\nRelation distribution:")
    for relation, count in sorted(relation_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {relation}: {count}")
    
    # Check for non-canonical relations
    canonical_relations = {
        "is_a", "defined_as", "part_of", "uses", "depends_on", "causes", 
        "enables", "prevents", "similar_to", "subset_of", "instance_of", 
        "associated_with", "located_in", "owned_by", "created_by", 
        "supports", "requires", "composed_of", "derived_from"
    }
    
    non_canonical = [rel for rel in relation_counts.keys() if rel not in canonical_relations]
    if non_canonical:
        print(f"⚠️  Non-canonical relations found: {non_canonical}")
    else:
        print("✓ All relations are canonical!")
    
    # Show some example triples
    print(f"\nExample triples:")
    for i, edge in enumerate(edges[:10]):  # Show first 10
        source_label = next((n["label"] for n in nodes if n["id"] == edge["source"]), "Unknown")
        target_label = next((n["label"] for n in nodes if n["id"] == edge["target"]), "Unknown")
        relation = edge["relation"]
        print(f"  {source_label} --{relation}--> {target_label}")

def test_qa_functionality():
    """Test the QA functionality with the ingested data."""
    print("\n=== Testing QA Functionality ===")
    
    test_questions = [
        "What is artificial intelligence?",
        "How does machine learning relate to AI?",
        "What technologies are used in deep learning?",
        "What is the relationship between neural networks and AI?"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/qa",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                cited_nodes = data.get("cited_nodes", [])
                cited_edges = data.get("cited_edges", [])
                
                print(f"Answer: {answer}")
                print(f"Cited nodes: {len(cited_nodes)}")
                print(f"Cited edges: {len(cited_edges)}")
            else:
                print(f"✗ QA failed with status {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error during QA: {e}")

def test_graph_retrieval():
    """Test retrieving the current graph state."""
    print("\n=== Testing Graph Retrieval ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/graph")
        
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            
            print(f"Current graph state:")
            print(f"  Nodes: {len(nodes)}")
            print(f"  Edges: {len(edges)}")
            
            # Show some sample nodes
            print(f"\nSample nodes:")
            for node in nodes[:5]:
                print(f"  - {node['label']}")
                
        else:
            print(f"✗ Graph retrieval failed with status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error during graph retrieval: {e}")

def main():
    """Run all tests."""
    print("Testing Triple Quality Improvements with Real-World Data")
    print("=" * 60)
    
    # Test API health
    if not test_api_health():
        print("API is not available. Please start the server first.")
        return
    
    # Test ingest with real URLs
    graph_data = test_ingest_sample_urls()
    
    if graph_data:
        # Test QA functionality
        test_qa_functionality()
        
        # Test graph retrieval
        test_graph_retrieval()
    
    print("\n" + "=" * 60)
    print("Real-world testing completed!")

if __name__ == "__main__":
    main()
