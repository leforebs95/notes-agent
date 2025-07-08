"""
Handwritten Notes MCP Server - Phase 1
Basic file operations and MCP server setup with Tool Registry system
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)
from loguru import logger

from config import (
    SERVER_NAME, 
    SERVER_VERSION, 
    RAW_DIR, 
    PROCESSED_DIR, 
    INDEX_DIR,
    LOG_FILE,
    LOG_LEVEL
)
from storage import DocumentStorage
from tool_handlers import tool_registry
from handlers import (
    ListRawFilesHandler,
    ListProcessedFilesHandler,
    ReadRawFileHandler,
    ReadProcessedFileHandler,
    GetDocumentInfoHandler,
    ListAllDocumentsHandler,
    CheckFilesNeedingProcessingHandler,
    GetServerStatusHandler,
    ProcessRawFileHandler,
)

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="10 MB", retention="10 days", level=LOG_LEVEL)

# Initialize MCP server
server = Server(SERVER_NAME)

# Initialize storage
storage = DocumentStorage()

# Register all tool handlers
def register_tool_handlers():
    """Register all tool handlers with the tool registry"""
    handlers = [
        ("list_raw_files", ListRawFilesHandler(storage)),
        ("list_processed_files", ListProcessedFilesHandler(storage)),
        ("read_raw_file", ReadRawFileHandler(storage)),
        ("read_processed_file", ReadProcessedFileHandler(storage)),
        ("get_document_info", GetDocumentInfoHandler(storage)),
        ("list_all_documents", ListAllDocumentsHandler(storage)),
        ("check_files_needing_processing", CheckFilesNeedingProcessingHandler(storage)),
        ("get_server_status", GetServerStatusHandler(storage)),
        ("process_raw_file", ProcessRawFileHandler(storage)),
    ]
    
    for name, handler in handlers:
        tool_registry.register(name, handler)

# Register handlers on import
register_tool_handlers()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the MCP server"""
    return tool_registry.get_tool_definitions()

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls from Claude Desktop using the tool registry"""
    return await tool_registry.execute_tool(name, arguments)

async def main():
    """Main function to run the MCP server"""
    logger.info(f"Starting {SERVER_NAME} MCP Server v{SERVER_VERSION}")
    logger.info(f"Raw files directory: {RAW_DIR}")
    logger.info(f"Processed files directory: {PROCESSED_DIR}")
    logger.info(f"Index directory: {INDEX_DIR}")
    
    # Ensure directories exist
    for directory in [RAW_DIR, PROCESSED_DIR, INDEX_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Run the server
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())