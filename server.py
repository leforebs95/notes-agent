"""
Handwritten Notes MCP Server - Phase 1
Basic file operations and MCP server setup
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
from anthropic import AsyncAnthropic

from config import (
    SERVER_NAME, 
    SERVER_VERSION, 
    RAW_DIR, 
    PROCESSED_DIR, 
    INDEX_DIR,
    LOG_FILE,
    LOG_LEVEL,
    ANTHROPIC_API_KEY
)
from storage import DocumentStorage

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="10 MB", retention="10 days", level=LOG_LEVEL)

# Initialize MCP server
server = Server(SERVER_NAME)

# Initialize storage
storage = DocumentStorage()

# Initialize Anthropic client
anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

async def process_raw_file(filename: str) -> str:
    """Process a raw file through LLM to improve formatting and fix OCR errors"""
    
    # Check if API key is available
    if not anthropic_client:
        return "Error: ANTHROPIC_API_KEY not configured. Please set the API key in your environment."
    
    # Check if file exists and needs processing
    raw_file = RAW_DIR / filename
    if not raw_file.exists():
        return f"Error: File '{filename}' not found in raw directory"
    
    # Read raw file content
    raw_content = storage.read_raw_file(filename)
    if raw_content is None:
        return f"Error: Could not read file '{filename}'"
    
    try:
        # Process the content through LLM
        logger.info(f"Processing file {filename} through LLM...")
        
        system_prompt = """You are a document processor that improves handwritten text that has been converted through OCR. Your task is to:

1. Fix OCR errors and typos
2. Improve formatting and structure
3. Maintain the original meaning and content
4. Organize the text into proper paragraphs
5. Fix punctuation and capitalization
6. Preserve important information like dates, names, numbers

Return only the cleaned and formatted text without any additional commentary or explanation."""

        response = await anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Please process and improve this handwritten text:\n\n{raw_content}"
                }
            ]
        )
        
        processed_content = response.content[0].text
        
        # Write processed content to file
        if storage.write_processed_file(filename, processed_content):
            # Update metadata
            storage.mark_file_processed(raw_file, PROCESSED_DIR / filename)
            
            return f"✅ Successfully processed '{filename}'\n\nProcessed content saved to: {PROCESSED_DIR / filename}\n\nPreview of processed content:\n{processed_content[:300]}{'...' if len(processed_content) > 300 else ''}"
        else:
            return f"Error: Failed to save processed content for '{filename}'"
    
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}")
        return f"Error processing file '{filename}': {str(e)}"

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for the MCP server"""
    return [
        Tool(
            name="list_raw_files",
            description="List all raw handwritten text files available for processing",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_processed_files",
            description="List all processed and cleaned text files",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="read_raw_file",
            description="Read the content of a raw handwritten text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="read_processed_file",
            description="Read the content of a processed/cleaned text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the processed file to read"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="get_document_info",
            description="Get metadata and processing information for a specific document",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the document to get info for"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="list_all_documents",
            description="List all documents with their metadata and processing status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="check_files_needing_processing",
            description="Check which files need processing (new or changed files)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_server_status",
            description="Get the current status of the MCP server and storage system",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="process_raw_file",
            description="Process a raw handwritten text file through LLM to improve formatting, fix typos, and correct OCR errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the raw file to process"
                    }
                },
                "required": ["filename"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls from Claude Desktop"""
    
    try:
        if name == "list_raw_files":
            raw_files = storage.get_raw_files()
            file_list = [f.name for f in raw_files]
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Found {len(file_list)} raw files:\n" + "\n".join(f"• {f}" for f in file_list)
                    )
                ]
            )
        
        elif name == "list_processed_files":
            processed_files = storage.get_processed_files()
            file_list = [f.name for f in processed_files]
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Found {len(file_list)} processed files:\n" + "\n".join(f"• {f}" for f in file_list)
                    )
                ]
            )
        
        elif name == "read_raw_file":
            filename = arguments.get("filename")
            if not filename:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: filename is required")]
                )
            
            content = storage.read_raw_file(filename)
            if content is None:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: Could not read file '{filename}' or file does not exist")]
                )
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Content of '{filename}':\n\n{content}"
                    )
                ]
            )
        
        elif name == "read_processed_file":
            filename = arguments.get("filename")
            if not filename:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: filename is required")]
                )
            
            content = storage.read_processed_file(filename)
            if content is None:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: Could not read processed file '{filename}' or file does not exist")]
                )
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Content of processed '{filename}':\n\n{content}"
                    )
                ]
            )
        
        elif name == "get_document_info":
            filename = arguments.get("filename")
            if not filename:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: filename is required")]
                )
            
            info = storage.get_document_info(filename)
            if info is None:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"No metadata found for '{filename}'")]
                )
            
            info_text = f"Document Information for '{filename}':\n\n"
            for key, value in info.items():
                info_text += f"• {key}: {value}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=info_text)]
            )
        
        elif name == "list_all_documents":
            all_docs = storage.list_all_documents()
            
            if not all_docs:
                return CallToolResult(
                    content=[TextContent(type="text", text="No documents found in the system")]
                )
            
            result_text = f"All Documents ({len(all_docs)} total):\n\n"
            for filename, info in all_docs.items():
                result_text += f"📄 {filename}\n"
                result_text += f"   Processed: {info.get('processed_at', 'Unknown')}\n"
                result_text += f"   Size: {info.get('size', 0)} bytes\n"
                result_text += f"   Hash: {info.get('hash', 'Unknown')[:8]}...\n\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
        
        elif name == "check_files_needing_processing":
            files_needing_processing = storage.get_files_needing_processing()
            
            if not files_needing_processing:
                return CallToolResult(
                    content=[TextContent(type="text", text="✅ All files are up to date - no processing needed")]
                )
            
            file_list = [f.name for f in files_needing_processing]
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"📋 Found {len(file_list)} files needing processing:\n" + "\n".join(f"• {f}" for f in file_list)
                    )
                ]
            )
        
        elif name == "get_server_status":
            raw_files = len(storage.get_raw_files())
            processed_files = len(storage.get_processed_files())
            files_needing_processing = len(storage.get_files_needing_processing())
            
            status_text = f"""🔧 Handwritten Notes MCP Server Status
            
Server: {SERVER_NAME} v{SERVER_VERSION}
Raw Files: {raw_files}
Processed Files: {processed_files}
Files Needing Processing: {files_needing_processing}

Directory Structure:
• Raw Files: {RAW_DIR}
• Processed Files: {PROCESSED_DIR}
• Index Files: {INDEX_DIR}

Status: ✅ Ready for Phase 2 development"""
            
            return CallToolResult(
                content=[TextContent(type="text", text=status_text)]
            )
        
        elif name == "process_raw_file":
            filename = arguments.get("filename")
            if not filename:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: filename is required")]
                )
            
            result = await process_raw_file(filename)
            return CallToolResult(
                content=[TextContent(type="text", text=result)]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error executing {name}: {str(e)}")]
        )

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