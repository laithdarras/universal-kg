#!/usr/bin/env python3
"""
Test script to verify triple quality improvements.
Tests the filtering of junk triples and canonical relation enforcement.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.helpers import extract_triples, normalize_label, STOPWORDS, BAD_ENTS, MIN_LEN, CANONICAL_RELATIONS
from api.graph_store import GraphStore, graph_store

def test_normalize_label():
    """Test the normalize_label function."""
    print("=== Testing normalize_label ===")
    
    test_cases = [
        ("Artificial Intelligence", "artificial intelligence"),
        ("The Machine Learning", "machine learning"),
        ("A Deep Learning System", "deep learning system"),
        ("There is an issue", "there is an issue"),
        ("  Neural Networks  ", "neural networks"),
        ("", ""),
        ("a", "a"),
    ]
    
    for input_text, expected in test_cases:
        result = normalize_label(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' -> '{result}' (expected: '{expected}')")

def test_junk_filtering():
    """Test filtering of junk entities."""
    print("\n=== Testing junk filtering ===")
    
    # Test cases that should be filtered out
    junk_entities = [
        "an", "the", "a", "there", "what", "not", "issue", "thing", 
        "something", "anything", "everything", "it", "they", "we"
    ]
    
    for entity in junk_entities:
        norm = normalize_label(entity)
        is_stopword = norm in STOPWORDS
        is_bad_ent = norm in BAD_ENTS
        too_short = len(norm) < MIN_LEN
        
        should_filter = is_stopword or is_bad_ent or too_short
        status = "✓" if should_filter else "✗"
        print(f"{status} '{entity}' (norm: '{norm}') - stopword: {is_stopword}, bad_ent: {is_bad_ent}, too_short: {too_short}")

def test_valid_entities():
    """Test that valid entities pass through."""
    print("\n=== Testing valid entities ===")
    
    valid_entities = [
        "Artificial Intelligence", "Machine Learning", "Deep Learning",
        "Neural Networks", "Natural Language Processing", "Computer Vision",
        "Data Science", "Robotics", "Python", "TensorFlow", "PyTorch"
    ]
    
    for entity in valid_entities:
        norm = normalize_label(entity)
        is_stopword = norm in STOPWORDS
        is_bad_ent = norm in BAD_ENTS
        too_short = len(norm) < MIN_LEN
        
        should_pass = not (is_stopword or is_bad_ent or too_short)
        status = "✓" if should_pass else "✗"
        print(f"{status} '{entity}' (norm: '{norm}') - should pass: {should_pass}")

def test_canonical_relations():
    """Test canonical relation validation."""
    print("\n=== Testing canonical relations ===")
    
    valid_relations = [
        "is_a", "defined_as", "part_of", "uses", "depends_on", "causes",
        "enables", "prevents", "similar_to", "subset_of", "instance_of"
    ]
    
    invalid_relations = [
        "is", "is an", "there is", "what is", "has", "does", "makes",
        "creates", "builds", "develops", "implements", "contains", "includes",
        "interacts_with", "generates", "produces", "improves", "enhances"
    ]
    
    print("Valid relations:")
    for relation in valid_relations:
        is_valid = relation in CANONICAL_RELATIONS
        status = "✓" if is_valid else "✗"
        print(f"{status} '{relation}'")
    
    print("\nInvalid relations:")
    for relation in invalid_relations:
        is_valid = relation in CANONICAL_RELATIONS
        status = "✓" if not is_valid else "✗"
        print(f"{status} '{relation}' (should be invalid)")

def test_triple_extraction():
    """Test triple extraction with junk filtering."""
    print("\n=== Testing triple extraction ===")
    
    test_texts = [
        "There is an artificial intelligence system that uses machine learning. Machine learning is a subset of artificial intelligence.",
        "The neural networks are part of deep learning. Deep learning uses artificial intelligence.",
        "A thing is something that exists. There is an issue with the system.",
        "Python is a programming language. TensorFlow is a machine learning framework. PyTorch is another framework."
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\nTest {i+1}: {text[:50]}...")
        triples = extract_triples(text, f"test_source_{i}")
        
        print(f"Extracted {len(triples)} triples:")
        for subject, relation, obj in triples:
            # Check if any junk got through
            subject_norm = normalize_label(subject)
            obj_norm = normalize_label(obj)
            
            subject_junk = subject_norm in STOPWORDS or subject_norm in BAD_ENTS or len(subject_norm) < MIN_LEN
            obj_junk = obj_norm in STOPWORDS or obj_norm in BAD_ENTS or len(obj_norm) < MIN_LEN
            relation_valid = relation in CANONICAL_RELATIONS
            
            status = "✓" if not (subject_junk or obj_junk) and relation_valid else "✗"
            print(f"{status} {subject} --{relation}--> {obj}")

def test_graph_store_cleanup():
    """Test graph store cleanup functionality."""
    print("\n=== Testing graph store cleanup ===")
    
    # Create a test graph store
    test_store = GraphStore()
    
    # Add some valid triples
    test_store.upsert_triple("Artificial Intelligence", "is_a", "Technology", "test_source", 0.8)
    test_store.upsert_triple("Machine Learning", "part_of", "Artificial Intelligence", "test_source", 0.9)
    test_store.upsert_triple("Deep Learning", "uses", "Neural Networks", "test_source", 0.7)
    
    # Add some junk triples (these should be filtered out by the extraction, but let's test cleanup)
    test_store.upsert_triple("an", "is", "thing", "test_source", 0.1)
    test_store.upsert_triple("there", "is", "issue", "test_source", 0.1)
    test_store.upsert_triple("what", "is", "something", "test_source", 0.1)
    
    print(f"Before cleanup: {len(test_store.graph.nodes())} nodes, {len(test_store.graph.edges())} edges")
    
    # Run cleanup
    removed_count = test_store.cleanup_junk_nodes()
    
    print(f"After cleanup: {len(test_store.graph.nodes())} nodes, {len(test_store.graph.edges())} edges")
    print(f"Removed {removed_count} junk nodes")
    
    # Check remaining nodes
    remaining_nodes = [attrs.get("label", "") for _, attrs in test_store.graph.nodes(data=True)]
    print(f"Remaining nodes: {remaining_nodes}")

def test_confidence_filtering():
    """Test confidence-based filtering."""
    print("\n=== Testing confidence filtering ===")
    
    # Test triples with different confidence levels
    test_triples = [
        {"subject": "Python", "relation": "is_a", "object": "Programming Language", "confidence": 0.9, "source": "test"},
        {"subject": "Machine Learning", "relation": "uses", "object": "Algorithms", "confidence": 0.7, "source": "test"},
        {"subject": "AI", "relation": "is_a", "object": "Technology", "confidence": 0.2, "source": "test"},  # Low confidence
        {"subject": "Deep Learning", "relation": "part_of", "object": "ML", "confidence": 0.1, "source": "test"},  # Very low confidence
    ]
    
    from api.helpers import _apply_post_process_filters
    
    filtered = _apply_post_process_filters(test_triples, "test_source")
    
    print(f"Input triples: {len(test_triples)}")
    print(f"Filtered triples: {len(filtered)}")
    
    for triple in filtered:
        confidence = triple.get("confidence", 0.0)
        print(f"✓ {triple['subject']} --{triple['relation']}--> {triple['object']} (confidence: {confidence})")
    
    # Verify that low-confidence triples are filtered out
    low_confidence_filtered = [t for t in filtered if t.get("confidence", 0.0) < 0.3]
    assert len(low_confidence_filtered) == 0, "Low confidence triples should be filtered out"
    print("✓ Confidence filtering working correctly")

def main():
    """Run all tests."""
    print("Testing Triple Quality Improvements")
    print("=" * 50)
    
    test_normalize_label()
    test_junk_filtering()
    test_valid_entities()
    test_canonical_relations()
    test_triple_extraction()
    test_graph_store_cleanup()
    test_confidence_filtering()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
