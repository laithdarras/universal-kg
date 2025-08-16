# Universal Knowledge Graph Frontend

A React frontend for the Universal Knowledge Graph API built with Vite, TypeScript, and React Flow.

## Features

- **URL Upload**: Paste URLs to build knowledge graphs
- **Graph Visualization**: Interactive graph using React Flow
- **Question & Answer**: Ask questions and see highlighted results
- **Node Details**: Click nodes to see detailed information
- **Dark Theme**: Modern dark UI with Tailwind CSS

## Setup

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload URLs**: Paste URLs in the left panel and click "Build Graph"
2. **View Graph**: The center panel shows the interactive knowledge graph
3. **Ask Questions**: Use the Q&A panel to ask questions about the graph
4. **Explore Nodes**: Click on nodes to see detailed information in the right panel

## Architecture

- **Components**: Modular React components for each panel
- **API Integration**: TypeScript API client for backend communication
- **State Management**: React hooks for local state
- **Styling**: Tailwind CSS for responsive design

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Dependencies

- React 18 with TypeScript
- Vite for fast development
- React Flow for graph visualization
- Tailwind CSS for styling
