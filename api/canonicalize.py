import re
from typing import Dict, Set

# Common aliases for canonicalization
ALIASES: Dict[str, str] = {
    "ai": "artificial intelligence",
    "ml": "machine learning", 
    "llm": "large language model",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "dl": "deep learning",
    "nn": "neural network",
    "neural networks": "neural network",
    "neural net": "neural network",
    "neural nets": "neural network",
    "artificial intelligence": "artificial intelligence",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "natural language processing": "natural language processing",
    "computer vision": "computer vision",
    "robotics": "robotics",
    "robotic": "robotics",
    "robot": "robotics"
}

def normalize_label(s: str) -> str:
    """Normalize a label for canonicalization."""
    if not s:
        return ""
    
    # Convert to lowercase and strip punctuation
    normalized = re.sub(r'[^\w\s]', ' ', s.lower())
    
    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Remove leading articles
    normalized = re.sub(r'^(a|an|the)\s+', '', normalized)
    
    return normalized

def canonical_form(s: str) -> str:
    """Get the canonical form of a label."""
    if not s:
        return ""
    
    normalized = normalize_label(s)
    
    # Check aliases first
    if normalized in ALIASES:
        return ALIASES[normalized]
    
    # Return normalized form if no alias found
    return normalized

def title_case(s: str) -> str:
    """Convert to title case for display."""
    if not s:
        return ""
    
    # Simple title case - capitalize first letter of each word
    return ' '.join(word.capitalize() for word in s.split())
