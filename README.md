# Universal Knowledge Graph API

A FastAPI backend that builds a knowledge graph from web content and provides question-answering capabilities.

## Features

- **URL Ingestion**: Fetch HTML content from URLs, extract text, and split into chunks
- **Triple Extraction**: Extract subject-relation-object triples from text chunks
- **Knowledge Graph**: Store triples in an in-memory networkx MultiDiGraph
- **Question Answering**: Answer questions by matching keywords against the knowledge graph

## API Endpoints

### 1. POST /api/ingest

Ingest URLs and extract knowledge triples.

**Request:**

```json
{
  "urls": ["https://example.com", "https://another-example.com"]
}
```

**Response:**

```json
{
  "nodes": [
    {
      "id": "uuid",
      "label": "entity_name",
      "type": "entity"
    }
  ],
  "edges": [
    {
      "id": "uuid",
      "source": "source_node_id",
      "target": "target_node_id",
      "relation": "relation_type",
      "sources": ["url#chunk_0"]
    }
  ]
}
```

### 2. GET /api/graph

Retrieve the current knowledge graph.

**Response:** Same format as ingest response.

### 3. POST /api/qa

Answer questions using the knowledge graph.

**Request:**

```json
{
  "question": "What is artificial intelligence?"
}
```

**Response:**

```json
{
  "answer": "Based on the available information...",
  "cited_nodes": ["node_id_1", "node_id_2"],
  "cited_edges": ["edge_id_1"]
}
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the server with auto-reload:

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

## Testing

Run the test script to verify all endpoints:

```bash
python test_api.py
```

## API Documentation

Once the server is running, visit:

- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Architecture

### Components

1. **`api/main.py`**: FastAPI application with all endpoints
2. **`api/graph_store.py`**: NetworkX graph management with upsert and DTO conversion
3. **`api/helpers.py`**: Helper functions for triple extraction and question answering

### Data Flow

1. **Ingestion**: URL → HTML → Text chunks → Triples → Graph storage
2. **Query**: Question → Keywords → Subgraph → Answer generation
3. **Storage**: In-memory NetworkX MultiDiGraph with deduplication

### Helper Functions

- `extract_triples(text, source_id)`: Currently stubbed with pattern matching
- `answer_question(question, subgraph)`: Currently stubbed with keyword matching

## Development

The helper functions are currently stubbed implementations. In a production system, you would:

1. Replace `extract_triples()` with proper NLP techniques (NER, relation extraction)
2. Replace `answer_question()` with more sophisticated reasoning algorithms
3. Add persistent storage for the knowledge graph
4. Implement proper error handling and validation
5. Add authentication and rate limiting

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- Requests: HTTP client
- BeautifulSoup4: HTML parsing
- NetworkX: Graph operations
- Pydantic: Data validation
- OpenAI: AI-powered triple extraction
- python-dotenv: Environment variable management

## OpenAI Integration

The system now supports OpenAI-powered triple extraction for more accurate knowledge graph building:

1. **Get an OpenAI API key** from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

2. **Set the environment variable**:

   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

   Or create a `.env` file in the root directory:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Features**:

   - Uses GPT-4o-mini for cost-effective extraction
   - Falls back to regex-based extraction if no API key
   - Handles large chunks gracefully (skips >4000 chars)
   - Robust JSON parsing with error handling
   - Deduplication and normalization of triples

4. **Without OpenAI**: The system works with regex-based extraction for basic triple extraction
