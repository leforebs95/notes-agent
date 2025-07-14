"""
Individual Tool Handlers for MCP Server
Each handler implements a specific tool functionality
"""

from typing import Dict, Any, List
from mcp.types import Tool, TextContent
from tool_handlers import BaseToolHandler
from config import SERVER_NAME, SERVER_VERSION, RAW_DIR, PROCESSED_DIR, INDEX_DIR


class ListRawFilesHandler(BaseToolHandler):
    """Handler for listing raw files"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        raw_files = self.storage.get_raw_files()
        file_list = [f.name for f in raw_files]
        text = f"Found {len(file_list)} raw files:\n" + "\n".join(
            f"• {f}" for f in file_list
        )
        return [TextContent(text=text)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="list_raw_files",
            description="List all raw handwritten text files available for processing",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )


class ListProcessedFilesHandler(BaseToolHandler):
    """Handler for listing processed files"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        processed_files = self.storage.get_processed_files()
        file_list = [f.name for f in processed_files]
        text = f"Found {len(file_list)} processed files:\n" + "\n".join(
            f"• {f}" for f in file_list
        )
        return [TextContent(text=text)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="list_processed_files",
            description="List all processed and cleaned text files",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )


class ReadRawFileHandler(BaseToolHandler):
    """Handler for reading raw files"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        if error := self.validate_required_args(arguments, ["filename"]):
            return self.create_text_response(error)

        filename = arguments["filename"]
        content = self.storage.read_raw_file(filename)
        if content is None:
            return self.create_text_response(
                f"Error: Could not read file '{filename}' or file does not exist"
            )

        return [TextContent(text=f"Content of '{filename}':\n\n{content}")]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="read_raw_file",
            description="Read the content of a raw handwritten text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to read",
                    }
                },
                "required": ["filename"],
            },
        )


class ReadProcessedFileHandler(BaseToolHandler):
    """Handler for reading processed files"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        if error := self.validate_required_args(arguments, ["filename"]):
            return [TextContent(text=error)]

        filename = arguments["filename"]
        content = self.storage.read_processed_file(filename)
        if content is None:
            return [TextContent(text=f"Error: Could not read processed file '{filename}' or file does not exist")]

        return [TextContent(text=f"Content of processed '{filename}':\n\n{content}")]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="read_processed_file",
            description="Read the content of a processed/cleaned text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the processed file to read",
                    }
                },
                "required": ["filename"],
            },
        )


class GetDocumentInfoHandler(BaseToolHandler):
    """Handler for getting document metadata"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        if error := self.validate_required_args(arguments, ["filename"]):
            return [TextContent(text=error)]

        filename = arguments["filename"]
        info = self.storage.get_document_info(filename)
        if info is None:
            return [TextContent(text=f"No metadata found for '{filename}'")]

        info_text = f"Document Information for '{filename}':\n\n"
        for key, value in info.items():
            info_text += f"• {key}: {value}\n"

        return [TextContent(text=info_text)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="get_document_info",
            description="Get metadata and processing information for a specific document",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the document to get info for",
                    }
                },
                "required": ["filename"],
            },
        )


class ListAllDocumentsHandler(BaseToolHandler):
    """Handler for listing all documents with metadata"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        all_docs = self.storage.list_all_documents()

        if not all_docs:
            return [TextContent(text="No documents found in the system")]

        result_text = f"All Documents ({len(all_docs)} total):\n\n"
        for filename, info in all_docs.items():
            result_text += f"📄 {filename}\n"
            result_text += f"   Processed: {info.get('processed_at', 'Unknown')}\n"
            result_text += f"   Size: {info.get('size', 0)} bytes\n"
            result_text += f"   Hash: {info.get('hash', 'Unknown')[:8]}...\n\n"

        return [TextContent(text=result_text)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="list_all_documents",
            description="List all documents with their metadata and processing status",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )


class CheckFilesNeedingProcessingHandler(BaseToolHandler):
    """Handler for checking which files need processing"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        files_needing_processing = self.storage.get_files_needing_processing()

        if not files_needing_processing:
            return [TextContent(text="All files are up to date - no processing needed")]

        file_list = [f.name for f in files_needing_processing]
        text = f"📋 Found {len(file_list)} files needing processing:\n" + "\n".join(
            f"• {f}" for f in file_list
        )
        return [TextContent(text=text)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="check_files_needing_processing",
            description="Check which files need processing (new or changed files)",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )


class GetServerStatusHandler(BaseToolHandler):
    """Handler for getting server status"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        raw_files = len(self.storage.get_raw_files())
        processed_files = len(self.storage.get_processed_files())
        files_needing_processing = len(self.storage.get_files_needing_processing())

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

        return [TextContent(text=status_text)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="get_server_status",
            description="Get the current status of the MCP server and storage system",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )


class ProcessRawFileHandler(BaseToolHandler):
    """Handler for processing raw files"""

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        if error := self.validate_required_args(arguments, ["filename"]):
            return [TextContent(text=error)]

        filename = arguments["filename"]
        result = await self.storage.process_raw_file(filename)
        return [TextContent(text=result)]

    def get_tool_definition(self) -> Tool:
        return Tool(
            name="process_raw_file",
            description="Process a raw handwritten text file through LLM to improve formatting, fix typos, and correct OCR errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the raw file to process",
                    }
                },
                "required": ["filename"],
            },
        )
