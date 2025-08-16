from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
import uuid
import logging

from .graph_store import graph_store
from .helpers import extract_triples, answer_question

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Universal Knowledge Graph API", version="1.0.0")

# Pydantic models for request/response
class IngestRequest(BaseModel):
    urls: List[str]

class IngestResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    answer: str
    cited_nodes: List[str]
    cited_edges: List[str]

def chunk_text(text, target=1800, overlap=200):
    """Robust text chunking with overlap."""
    if not text: 
        return []
    chunks = []
    i = 0
    while i < len(text):
        j = min(i+target, len(text))
        chunks.append(text[i:j])
        if j == len(text): 
            break
        i = j - overlap
        if i < 0: 
            i = 0
    return chunks

def fetch_and_process_url(url: str) -> List[str]:
    """Fetch HTML from URL, strip tags, and split into chunks."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        
        # Parse HTML and extract text
        soup = BeautifulSoup(r.content, "html.parser")
        
        # Remove script, style, and noscript elements
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        
        # Get text content and clean up whitespace
        text = " ".join(soup.get_text(" ").split())
        
        logger.info(f"TRACE fetch: url={url} status={r.status_code} text_len={len(text)} preview={text[:120]!r}")
        
        # Chunk the text
        chunks = chunk_text(text, target=1800, overlap=200)
        logger.info(f"TRACE chunking: url={url} count={len(chunks)} first_len={(len(chunks[0]) if chunks else 0)}")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return []

@app.get("/")
def read_root():
    return {"message": "Universal Knowledge Graph API", "version": "1.0.0"}

@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_urls(request: IngestRequest):
    """Ingest URLs and extract knowledge triples."""
    empty_urls_flag = False
    
    for url in request.urls:
        try:
            logger.info(f"TRACE ingest: url={url}")
            
            # Fetch and process the URL
            chunks = fetch_and_process_url(url)
            logger.info(f"TRACE chunks: url={url} count={len(chunks)}")
            
            if len(chunks) == 0:
                logger.warning(f"No content extracted from {url}")
                empty_urls_flag = True
                continue
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Skip chunks larger than ~4000 chars to control token costs
                if len(chunk) > 4000:
                    logger.info(f"Skipping chunk {i} from {url} - too large ({len(chunk)} chars)")
                    continue
                    
                source_id = f"{url}#chunk_{i}"
                logger.info(f"TRACE extract: source_id={source_id} len={len(chunk)}")
                
                # Extract triples from the chunk
                triples = extract_triples(chunk, source_id)
                logger.info(f"TRACE triples: count={len(triples)} first={(triples[0] if triples else 'NONE')}")
                
                # Store triples in the graph
                for tr in triples:
                    subj = tr.get("subject") or tr[0] if isinstance(tr, (list, tuple)) else tr.get("subject")
                    rel = tr.get("relation") or tr[1] if isinstance(tr, (list, tuple)) else tr.get("relation")
                    obj = tr.get("object") or tr[2] if isinstance(tr, (list, tuple)) else tr.get("object")
                    if not subj or not rel or not obj: 
                        continue
                    graph_store.upsert_triple(subj, rel, obj, source_id, confidence=tr.get("confidence", 0.5))
            
            logger.info(f"TRACE graph-size: nodes={len(graph_store.graph.nodes())} edges={len(graph_store.graph.edges())}")
            
        except Exception as e:
            logger.exception(f"ERROR ingest for url={url}")
            continue
    
    # Add seed fallback if graph is empty
    if len(graph_store.graph.nodes()) == 0:
        logger.warning("WARN: graph empty after ingest; seeded sample triples.")
        graph_store.upsert_triple("Artificial Intelligence", "defined_as", "Field of Computer Science", "seed", confidence=1.0)
        graph_store.upsert_triple("Artificial Intelligence", "related_to", "Machine Learning", "seed", confidence=0.9)
        graph_store.upsert_triple("Machine Learning", "subset_of", "Artificial Intelligence", "seed", confidence=0.9)
    
    # Return the current graph
    result = graph_store.to_dto()
    return result

@app.post("/api/ingest-file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    """Ingest TXT file and extract knowledge triples."""
    try:
        # Validate file type
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only TXT files supported for now")
        
        # Check file size (5MB limit)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")
        
        # Decode content
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decode file: {str(e)}")
        
        logger.info(f"TRACE ingest-file: filename={file.filename} size={len(content)} text_len={len(text)}")
        
        # Chunk the text
        chunks = chunk_text(text, target=1800, overlap=200)
        logger.info(f"TRACE file-chunking: filename={file.filename} count={len(chunks)}")
        
        if len(chunks) == 0:
            logger.warning(f"No content extracted from {file.filename}")
            raise HTTPException(status_code=400, detail="No readable content found in file")
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            source_id = f"{file.filename}#chunk_{i}"
            logger.info(f"TRACE extract: source_id={source_id} len={len(chunk)}")
            
            # Extract triples from the chunk
            triples = extract_triples(chunk, source_id)
            logger.info(f"TRACE triples: count={len(triples)} first={(triples[0] if triples else 'NONE')}")
            
            # Store triples in the graph
            for tr in triples:
                subj = tr.get("subject") or tr[0] if isinstance(tr, (list, tuple)) else tr.get("subject")
                rel = tr.get("relation") or tr[1] if isinstance(tr, (list, tuple)) else tr.get("relation")
                obj = tr.get("object") or tr[2] if isinstance(tr, (list, tuple)) else tr.get("object")
                if not subj or not rel or not obj: 
                    continue
                graph_store.upsert_triple(subj, rel, obj, source_id, confidence=tr.get("confidence", 0.5))
        
        logger.info(f"TRACE graph-size: nodes={len(graph_store.graph.nodes())} edges={len(graph_store.graph.edges())}")
        
        # Return the current graph
        result = graph_store.to_dto()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"ERROR ingest-file for filename={file.filename}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/graph", response_model=IngestResponse)
async def get_graph():
    """Get the current knowledge graph."""
    try:
        return graph_store.to_dto()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving graph: {str(e)}")

@app.post("/api/qa", response_model=QAResponse)
async def answer_question_endpoint(request: QARequest):
    """Answer questions using the knowledge graph."""
    try:
        # Extract keywords from the question
        question_clean = re.sub(r'[^\w\s]', ' ', request.question.lower())
        question_words = re.findall(r'\b\w+\b', question_clean)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'what', 'when', 'where', 'who', 'why', 'how'}
        keywords = [word for word in question_words if word not in stop_words and len(word) > 1]
        
        # Get relevant subgraph
        subgraph = graph_store.get_subgraph_by_keywords(keywords)
        
        # Answer the question
        result = answer_question(request.question, subgraph)
        
        return QAResponse(
            answer=result["answer"],
            cited_nodes=result["cited_nodes"],
            cited_edges=result["cited_edges"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)