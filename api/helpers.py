from typing import List, Dict, Any, Tuple
import re
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import networkx as nx

# Load environment variables
load_dotenv()

# Initialize OpenAI client (will be None if no API key)
openai_client = None
try:
    if os.getenv("OPENAI_API_KEY"):
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("INFO OpenAI client: enabled")
    else:
        print("INFO OpenAI client: missing, fallback")
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    openai_client = None

def extract_triples(text: str, source_id: str, max_triples: int = 8) -> List[Dict[str, Any]]:
    """
    Extract subject-relation-object triples from text using OpenAI.
    Falls back to stub implementation if no API key or parsing fails.
    Returns List[Dict] with keys: subject, relation, object, confidence, source
    """
    print(f"TRACE extract_triples: source={source_id} len={len(text)}")
    
    # If no OpenAI API key, fall back to stub implementation
    if not openai_client:
        print("DEBUG: No OpenAI client, using stub")
        return _extract_triples_stub(text, source_id)
    
    # Truncate text if too large for the model
    if len(text) > 3500:
        text = text[:3500]
        print("DEBUG: Text truncated to 3500 chars for model")
    
    try:
        # Create the prompt for OpenAI
        prompt = f"""Extract factual triples from this text. Return ONLY valid JSON with this exact schema:

{{
  "triples": [
    {{"subject":"<Concept>","relation":"<Relation>","object":"<Concept>","confidence":0.0,"source":"{source_id}"}}
  ]
}}

Rules:
- Subjects and objects should be specific concepts, entities, or technologies
- Relations should be meaningful relationships like "is_a", "uses", "depends_on", "enables", etc.
- Avoid generic relations like "is", "has", "contains"
- Cap to {max_triples} triples maximum
- Confidence should be between 0.0 and 1.0

Text: {text}"""

        print("DEBUG: Calling OpenAI API...")
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        print(f"DEBUG: OpenAI response: {content}")
        
        # Try to parse JSON response
        try:
            data = json.loads(content)
            triples = []
            
            if "triples" in data:
                for triple in data["triples"]:
                    if all(key in triple for key in ["subject", "relation", "object"]):
                        triples.append({
                            "subject": triple["subject"].strip(),
                            "relation": triple["relation"].strip(),
                            "object": triple["object"].strip(),
                            "confidence": triple.get("confidence", 0.5),
                            "source": source_id
                        })
            
            print(f"DEBUG: extract_triples returning {len(triples)} triples")
            return triples[:max_triples]
            
        except json.JSONDecodeError:
            print(f"WARN: Failed to parse JSON from OpenAI response: {content[:80]}")
            return _extract_triples_stub(text, source_id)
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return _extract_triples_stub(text, source_id)

def _extract_triples_stub(text: str, source_id: str) -> List[Dict[str, Any]]:
    """Stub implementation for triple extraction when OpenAI is not available."""
    print("DEBUG: _extract_triples_stub called")
    # Simple rule-based extraction
    triples = []
    
    # Look for common patterns
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 10:
            continue
            
        # Pattern: "X is a Y"
        match = re.search(r'(\w+(?:\s+\w+)*)\s+is\s+a\s+(\w+(?:\s+\w+)*)', sentence, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            if len(subject) > 2 and len(obj) > 2:
                triples.append({
                    "subject": subject,
                    "relation": "is_a",
                    "object": obj,
                    "confidence": 0.7,
                    "source": source_id
                })
        
        # Pattern: "X uses Y"
        match = re.search(r'(\w+(?:\s+\w+)*)\s+uses\s+(\w+(?:\s+\w+)*)', sentence, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            if len(subject) > 2 and len(obj) > 2:
                triples.append({
                    "subject": subject,
                    "relation": "uses",
                    "object": obj,
                    "confidence": 0.7,
                    "source": source_id
                })
        
        # Pattern: "X depends on Y"
        match = re.search(r'(\w+(?:\s+\w+)*)\s+depends\s+on\s+(\w+(?:\s+\w+)*)', sentence, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            obj = match.group(2).strip()
            if len(subject) > 2 and len(obj) > 2:
                triples.append({
                    "subject": subject,
                    "relation": "depends_on",
                    "object": obj,
                    "confidence": 0.7,
                    "source": source_id
                })
    
    print(f"DEBUG: _extract_triples_stub returning {len(triples)} triples")
    return triples[:8]  # Cap to 8 triples

def answer_question(question: str, graph_store) -> Dict[str, Any]:
    """Answer a question using the knowledge graph."""
    if not graph_store.graph.nodes():
        return {
            "answer": "I don't have enough information to answer this question.",
            "cited_nodes": [],
            "cited_edges": []
        }
    
    # Simple keyword-based answer generation
    question_lower = question.lower()
    
    # Find relevant nodes
    relevant_nodes = []
    for node_id, attrs in graph_store.graph.nodes(data=True):
        label = attrs.get("label", "").lower()
        if any(word in label for word in question_lower.split()):
            relevant_nodes.append(node_id)
    
    # Find relevant edges
    relevant_edges = []
    for source, target, edge_id, attrs in graph_store.graph.edges(data=True, keys=True):
        relation = attrs.get("relation", "").lower()
        if any(word in relation for word in question_lower.split()):
            relevant_edges.append(edge_id)
    
    # Generate a simple answer
    if relevant_nodes:
        node_labels = [graph_store.graph.nodes[node_id]["label"] for node_id in relevant_nodes[:3]]
        answer = f"Based on the knowledge graph, I found information about: {', '.join(node_labels)}"
    else:
        answer = "I couldn't find specific information to answer your question."
    
    return {
        "answer": answer,
        "cited_nodes": relevant_nodes,
        "cited_edges": relevant_edges
    }
