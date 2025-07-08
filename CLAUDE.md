# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for managing handwritten notes that transforms OCR/transcribed text into an intelligent, searchable knowledge base. The system integrates with Claude Desktop to provide conversational access to processed notes with proper citations.

## Development Commands

### Running the Server
```bash
python server.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
# Or with uv:
uv sync
```

### Testing the Server
Place test files in `data/raw/` directory and interact through Claude Desktop with configured MCP server.

## Architecture

### Core Components

1. **MCP Server** (`server.py`): Main server handling Claude Desktop communication
   - Provides 8 tools for file management and document operations
   - Uses asyncio and MCP protocol for tool execution
   - Handles all client-server communication

2. **Document Storage** (`storage.py`): File management and metadata tracking
   - Tracks document processing state with MD5 hashes
   - Manages raw/processed file operations
   - Maintains JSON metadata in `data/index/document_metadata.json`

3. **Configuration** (`config.py`): Central configuration management
   - Defines directory structure (`data/raw/`, `data/processed/`, `data/index/`)
   - Manages API keys and processing settings
   - Configures logging and server parameters

### Data Flow

1. Raw handwritten text files placed in `data/raw/`
2. System tracks file changes using MD5 hashes
3. Files processed through LLM cleanup (Phase 2 - not yet implemented)
4. Processed files stored in `data/processed/`
5. Search indexes built for keyword/semantic search (Phase 3 - not yet implemented)

### Directory Structure

```
data/
├── raw/          # Original handwritten text files
├── processed/    # Cleaned and processed documents  
└── index/        # Search indexes and metadata
```

## Development Status

**Phase 1: Basic MCP Server ✅**
- Core MCP server implementation complete
- File operations and metadata tracking working
- Claude Desktop integration functional

**Phase 2: Document Processing (In Progress)**
- LLM-powered text cleanup using Anthropic API
- Document chunking and processing pipeline
- Needs implementation of document processor module

**Phase 3: Search Implementation (Planned)**
- Keyword search with fuzzy matching
- Semantic search using sentence transformers
- Hybrid search result ranking

**Phase 4: Citation System (Planned)**
- Source tracking and reference management
- Citation formatting in responses

## Available MCP Tools

- `list_raw_files()` - List files in raw directory
- `list_processed_files()` - List processed files
- `read_raw_file(filename)` - Read raw file content
- `read_processed_file(filename)` - Read processed file content
- `get_document_info(filename)` - Get file metadata
- `list_all_documents()` - List all documents with metadata
- `check_files_needing_processing()` - Check which files need processing
- `get_server_status()` - Get server and storage status

## Configuration Requirements

### Environment Variables
- `ANTHROPIC_API_KEY` - Required for document processing (Phase 2+)

### Claude Desktop Configuration
Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "handwritten-notes": {
      "command": "python",
      "args": ["path/to/notes-agent/server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Key Implementation Details

### File Processing Logic
- Uses MD5 hashes to track file changes in `storage.py:file_needs_processing()`
- Metadata stored as JSON with processing timestamps
- Supports `.txt`, `.md`, `.text` file extensions

### Error Handling
- Comprehensive exception handling in all tool calls
- Logging configured with loguru (rotating 10MB files, 10-day retention)
- Graceful fallbacks for missing files/metadata

### Future Extension Points
- Document processor module for LLM text cleanup
- Search engine module for keyword/semantic search
- Citation system for source tracking
- Real-time file monitoring for automatic processing