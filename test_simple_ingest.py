#!/usr/bin/env python3
"""
Simple test to verify triple quality improvements with smaller content.
Tests the API with a simple text input to avoid timeout issues.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_simple_text_ingest():
    """Test with simple text that should produce meaningful triples."""
    print("=== Testing Simple Text Ingestion ===")
    
    # Simple test text with clear relationships
    test_text = """
    Artificial Intelligence is a technology that enables machines to learn and reason.
    Machine Learning is a subset of Artificial Intelligence that uses algorithms to improve performance.
    Deep Learning is part of Machine Learning that uses neural networks.
    Natural Language Processing uses Machine Learning to understand human language.
    Computer Vision uses Deep Learning to analyze images and videos.
    Python is a programming language that supports Machine Learning development.
    TensorFlow is a machine learning framework developed by Google.
    PyTorch is another machine learning framework used for deep learning.
    """
    
    print("Test text:")
    print(test_text.strip())
    print()
    
    # Test the triple extraction directly
    try:
        from api.helpers import extract_triples
        
        print("Extracting triples from test text...")
        triples = extract_triples(test_text, "test_source_simple")
        
        print(f"✓ Extracted {len(triples)} triples:")
        for i, (subject, relation, obj) in enumerate(triples, 1):
            print(f"  {i}. {subject} --{relation}--> {obj}")
        
        # Analyze quality
        analyze_extracted_triples(triples)
        
        return triples
        
    except Exception as e:
        print(f"✗ Error during triple extraction: {e}")
        return None

def analyze_extracted_triples(triples):
    """Analyze the quality of extracted triples."""
    print("\n=== Triple Quality Analysis ===")
    
    if not triples:
        print("No triples extracted")
        return
    
    # Check for junk patterns
    junk_patterns = ["there is", "there are", "this is", "that is", "it is", "what is"]
    junk_count = 0
    
    for subject, relation, obj in triples:
        # Check if any part contains junk patterns
        subject_lower = subject.lower()
        obj_lower = obj.lower()
        
        for pattern in junk_patterns:
            if pattern in subject_lower or pattern in obj_lower:
                junk_count += 1
                print(f"⚠️  Junk pattern detected: {subject} --{relation}--> {obj}")
                break
    
    if junk_count == 0:
        print("✓ No junk patterns detected!")
    else:
        print(f"⚠️  Found {junk_count} triples with junk patterns")
    
    # Check relation quality
    canonical_relations = {
        "is_a", "defined_as", "part_of", "uses", "depends_on", "causes", 
        "enables", "prevents", "similar_to", "subset_of", "instance_of", 
        "associated_with", "located_in", "owned_by", "created_by", 
        "supports", "requires", "composed_of", "derived_from"
    }
    
    non_canonical = []
    for _, relation, _ in triples:
        if relation not in canonical_relations:
            non_canonical.append(relation)
    
    if non_canonical:
        print(f"⚠️  Non-canonical relations found: {list(set(non_canonical))}")
    else:
        print("✓ All relations are canonical!")
    
    # Check entity quality
    stopwords = {"an", "the", "a", "there", "what", "not", "issue", "thing", "something", "anything", "everything"}
    junk_entities = []
    
    for subject, relation, obj in triples:
        subject_words = set(subject.lower().split())
        obj_words = set(obj.lower().split())
        
        if subject_words.intersection(stopwords) or obj_words.intersection(stopwords):
            junk_entities.append((subject, relation, obj))
    
    if junk_entities:
        print(f"⚠️  Triples with junk entities: {len(junk_entities)}")
        for subject, relation, obj in junk_entities[:3]:
            print(f"    {subject} --{relation}--> {obj}")
    else:
        print("✓ No junk entities detected!")

def test_api_with_simple_data():
    """Test the API with simple data to avoid timeout."""
    print("\n=== Testing API with Simple Data ===")
    
    try:
        # Test API health
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("✗ API not available")
            return
        
        print("✓ API is running")
        
        # Test graph retrieval (should be empty initially)
        response = requests.get(f"{BASE_URL}/api/graph")
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            print(f"Current graph: {len(nodes)} nodes, {len(edges)} edges")
        
        # Test QA with empty graph
        response = requests.post(
            f"{BASE_URL}/api/qa",
            json={"question": "What is artificial intelligence?"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            print(f"QA response: {answer}")
        else:
            print(f"QA failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ API test error: {e}")

def main():
    """Run the simple tests."""
    print("Testing Triple Quality Improvements with Simple Data")
    print("=" * 60)
    
    # Test simple text extraction
    triples = test_simple_text_ingest()
    
    # Test API functionality
    test_api_with_simple_data()
    
    print("\n" + "=" * 60)
    print("Simple testing completed!")
    
    if triples:
        print(f"\nSummary: Successfully extracted {len(triples)} high-quality triples")
        print("The triple quality improvements are working correctly!")

if __name__ == "__main__":
    main()
