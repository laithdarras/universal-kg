# Universal Knowledge Graph Explorer

A powerful web application that automatically extracts knowledge triples from URLs and text files, builds interactive knowledge graphs, and provides intelligent question answering capabilities.

## 🌟 Features

- **URL Processing**: Extract knowledge from web pages with intelligent HTML parsing
- **File Upload**: Support for TXT file uploads (up to 5MB)
- **Interactive Graph Visualization**: Beautiful, interactive knowledge graph with React Flow
- **Intelligent Question Answering**: Ask questions and get answers based on the knowledge graph
- **Entity Canonicalization**: Automatic merging of duplicate entities (e.g., "AI" and "Artificial Intelligence")
- **Real-time Graph Updates**: Dynamic graph building and visualization
- **Node Details Panel**: Explore connections and relationships for any node

## 🏗️ Architecture

- **Backend**: FastAPI + NetworkX + OpenAI API
- **Frontend**: React + TypeScript + React Flow + Tailwind CSS
- **Knowledge Extraction**: OpenAI GPT-3.5-turbo for triple extraction
- **Graph Storage**: In-memory NetworkX graph with persistent node/edge mapping

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd universal-kg
   ```

2. **Set up Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend**

   ```bash
   cd app
   npm install
   ```

4. **Configure environment**
   ```bash
   # Set your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   # On Windows: set OPENAI_API_KEY=your-api-key-here
   ```

### Running the Application

1. **Start the backend**

   ```bash
   uvicorn api.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

2. **Start the frontend** (in a new terminal)
   ```bash
   cd app
   npm run dev
   ```
   The application will be available at `http://localhost:3000`

## 📖 Usage Guide

### Uploading Content

#### URL Processing

1. Click the "🔗 URLs" tab
2. Enter one or more URLs (one per line)
3. Click "Build Graph"
4. Watch as the knowledge graph is automatically generated

#### File Upload

1. Click the "📄 TXT File" tab
2. Click "Choose File" and select a TXT file (max 5MB)
3. The file will be automatically processed and added to the graph

### Exploring the Graph

- **Zoom**: Use mouse wheel or zoom controls
- **Pan**: Click and drag to move around
- **Node Selection**: Click any node to see its details
- **Search**: Use the search bar to find specific nodes
- **Question Answering**: Ask questions in the QA panel

### Asking Questions

1. Type your question in the "Ask Questions" panel
2. Click "Ask"
3. Get answers based on the knowledge graph content
4. Cited nodes and edges will be highlighted in the graph

## 🔧 API Documentation

### Endpoints

#### `POST /api/ingest`

Process URLs and extract knowledge triples.

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
      "id": "node-id",
      "label": "Entity Name",
      "type": "entity"
    }
  ],
  "edges": [
    {
      "id": "edge-id",
      "source": "source-node-id",
      "target": "target-node-id",
      "relation": "relationship_type",
      "sources": ["source-url"]
    }
  ]
}
```

#### `POST /api/ingest-file`

Upload and process TXT files.

**Request:** Multipart form data with file field

**Response:** Same as `/api/ingest`

#### `GET /api/graph`

Get the current knowledge graph.

**Response:** Same as `/api/ingest`

#### `POST /api/qa`

Ask questions about the knowledge graph.

**Request:**

```json
{
  "question": "What is artificial intelligence?"
}
```

**Response:**

```json
{
  "answer": "Based on the knowledge graph...",
  "cited_nodes": ["node-id-1", "node-id-2"],
  "cited_edges": ["edge-id-1"]
}
```

## 🏛️ Project Structure

```
universal-kg/
├── api/                    # Backend API
│   ├── main.py            # FastAPI application
│   ├── helpers.py         # Triple extraction and QA logic
│   ├── graph_store.py     # Graph storage and management
│   └── canonicalize.py    # Entity canonicalization
├── app/                   # Frontend React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── lib/          # API client and utilities
│   │   └── main.tsx      # Application entry point
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔍 Knowledge Extraction Process

1. **Content Fetching**: URLs are fetched with proper headers and timeouts
2. **Text Processing**: HTML is parsed and cleaned using BeautifulSoup
3. **Chunking**: Text is split into manageable chunks (1800 chars with 200 char overlap)
4. **Triple Extraction**: OpenAI GPT-3.5-turbo extracts structured triples
5. **Canonicalization**: Entities are normalized and merged
6. **Graph Building**: Triples are stored in a NetworkX graph
7. **Visualization**: React Flow renders the interactive graph

## 🎯 Triple Quality

The system uses intelligent filtering to ensure high-quality triples:

- **Entity Validation**: Minimum length requirements and stopword filtering
- **Relation Canonicalization**: Standardized relationship types
- **Confidence Scoring**: Each triple includes a confidence score
- **Source Tracking**: All triples are linked to their source URLs/files

## 🛠️ Development

### Backend Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd app
npm install
npm run dev
```

### Testing

```bash
# Test the API
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://en.wikipedia.org/wiki/Artificial_intelligence"]}'
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)

### File Upload Limits

- **Maximum file size**: 5MB
- **Supported formats**: TXT files only
- **Encoding**: UTF-8 (with fallback handling)

## 🚨 Troubleshooting

### Common Issues

1. **Graph not rendering**

   - Check browser console for errors
   - Verify backend is running on port 8000
   - Ensure OpenAI API key is set

2. **File upload fails**

   - Check file size (max 5MB)
   - Ensure file is TXT format
   - Verify backend is running

3. **No triples extracted**
   - Check OpenAI API key and quota
   - Verify URL is accessible
   - Check backend logs for errors

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment.

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, React, and OpenAI**
