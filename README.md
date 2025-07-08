# Handwritten Notes MCP Server

A Model Context Protocol (MCP) server that transforms handwritten notes into an intelligent, searchable knowledge base using Claude Desktop.

## Purpose & Goals

This project addresses the challenge of managing handwritten notes that have been converted to text through OCR or transcription services. The conversion process often introduces errors, making the notes difficult to search and reference. This MCP server creates an intelligent pipeline that:

1. **Cleans and improves** OCR/transcription errors using LLM-powered text correction
2. **Indexes documents** for both keyword and semantic search
3. **Enables natural conversation** over your notes with proper citations
4. **Maintains source references** to original documents for verification

## How It Works

The MCP server integrates directly with Claude Desktop, providing a seamless chat interface for interacting with your handwritten notes. The workflow consists of:

1. **Document Ingestion**: Place handwritten text files in the monitored directory
2. **Text Cleanup**: Process files through Claude to fix OCR errors and improve readability
3. **Intelligent Indexing**: Create both keyword and semantic search indexes
4. **Conversational Access**: Ask questions about your notes through Claude Desktop
5. **Source Citation**: Get answers with references to original documents

## Key Features

- **LLM-Powered Text Correction**: Automatically fixes common OCR errors and improves text quality
- **Dual Search Capabilities**: Combines keyword matching with semantic understanding
- **Citation System**: All responses include references to source documents
- **Claude Desktop Integration**: Natural conversation interface through MCP protocol
- **Local Processing**: All data remains on your local machine
- **Incremental Processing**: Only processes new or changed files

## Architecture

The system consists of four main components:

1. **MCP Server** (`server.py`): Handles communication with Claude Desktop
2. **Document Processor** (`document_processor.py`): Cleans and improves text quality
3. **Search Engine** (`search_engine.py`): Provides keyword and semantic search
4. **Storage System** (`storage.py`): Manages document indexing and retrieval

## Project Structure

```
handwritten-notes-mcp/
├── README.md                 # This file
├── server.py                 # Main MCP server implementation
├── document_processor.py     # Text cleanup and processing logic
├── search_engine.py          # Keyword and semantic search engine
├── storage.py               # Document storage and indexing
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── claude_desktop_config.json # Claude Desktop MCP configuration
└── data/
    ├── raw/                 # Original handwritten text files
    ├── processed/           # Cleaned and processed documents
    └── index/               # Search index files
```

## Use Cases

- **Research Notes**: Convert handwritten research notes into searchable knowledge base
- **Meeting Minutes**: Process handwritten meeting notes for easy reference
- **Journal Entries**: Make personal journals searchable and conversational
- **Study Notes**: Transform handwritten study materials into interactive learning tool
- **Creative Writing**: Organize and search through handwritten story ideas and drafts

## Development Phases

### Phase 1: Basic MCP Server ✅
- Set up MCP server structure
- Implement basic file operations
- Test Claude Desktop integration

### Phase 2: Document Processing (In Progress)
- Add text cleanup using Claude API
- Implement document chunking
- Add processed document storage

### Phase 3: Search Implementation
- Implement keyword search
- Add semantic search with embeddings
- Combine and rank search results

### Phase 4: Citation System
- Add source tracking
- Implement citation formatting
- Complete end-to-end workflow

## Installation & Setup

### Prerequisites
- Python 3.8+
- Claude Desktop installed
- Anthropic API key (for text cleanup)

### Installation Steps

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure Claude Desktop to use the MCP server (see Configuration section)
4. Place your handwritten text files in the `data/raw/` directory
5. Start using the server through Claude Desktop

## Configuration

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "handwritten-notes": {
      "command": "python",
      "args": ["path/to/handwritten-notes-mcp/server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Commands

Once integrated with Claude Desktop, you can use these commands:

- `process_new_documents()` - Process any new files in the raw directory
- `search_documents(query)` - Search through processed documents
- `list_documents()` - Show all processed documents
- `get_document_info(filename)` - Get details about a specific document
- `cleanup_document(filename)` - Manually clean a specific document

## Technical Details

### Text Cleanup Process
The document processor uses Claude to:
- Fix common OCR errors (character misrecognition, spacing issues)
- Improve punctuation and formatting
- Preserve original meaning while enhancing readability
- Maintain document structure and formatting

### Search Implementation
- **Keyword Search**: Fast text matching with fuzzy matching capabilities
- **Semantic Search**: Uses sentence transformers to understand meaning
- **Hybrid Results**: Combines and ranks results from both search methods

### Citation System
Every search result includes:
- Source document filename
- Relevant text excerpt
- Context from surrounding paragraphs
- Confidence score for relevance

## Contributing

This project is designed as a personal knowledge management tool. Feel free to:
- Modify search algorithms for your specific needs
- Add new document processing capabilities
- Extend the MCP server with additional tools
- Improve the citation and reference system

## Future Enhancements

- Real-time file monitoring for automatic processing
- Support for additional file formats (PDF, images)
- Advanced document categorization and tagging
- Integration with external note-taking applications
- Export capabilities for processed documents

## License

This project is intended for personal use. Modify and adapt as needed for your specific requirements.