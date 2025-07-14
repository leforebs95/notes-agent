"""
Tool Registry and Base Handler Classes for MCP Server
Provides a structured approach to managing tool handlers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Awaitable
from mcp.types import ContentBlock, Tool
from loguru import logger


class BaseToolHandler(ABC):
    """Base class for all tool handlers with common functionality"""

    def __init__(self, storage):
        self.storage = storage

    @abstractmethod
    async def execute(
        self, arguments: Dict[str, Any]
    ) -> List[ContentBlock]:
        """Execute the tool with given arguments"""
        pass

    @abstractmethod
    def get_tool_definition(self) -> Tool:
        """Return the tool definition for MCP server registration"""
        pass

    def validate_required_args(
        self, arguments: Dict[str, Any], required: List[str]
    ) -> Optional[str]:
        """Validate that required arguments are present and non-empty"""
        for arg in required:
            if not arguments.get(arg):
                return f"Error: {arg} is required"
        return None


class ToolRegistry:
    """Registry for managing tool handlers"""

    def __init__(self):
        self._handlers: Dict[str, BaseToolHandler] = {}

    def register(self, name: str, handler: BaseToolHandler):
        """Register a tool handler"""
        self._handlers[name] = handler
        logger.debug(f"Registered tool handler: {name}")

    def get_handler(self, name: str) -> Optional[BaseToolHandler]:
        """Get a tool handler by name"""
        return self._handlers.get(name)

    def list_tool_names(self) -> List[str]:
        """List all registered tool names"""
        return list(self._handlers.keys())

    def get_tool_definitions(self) -> List[Tool]:
        """Get all tool definitions for MCP server registration"""
        return [handler.get_tool_definition() for handler in self._handlers.values()]

    async def execute_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[TextContent | ImageContent | AudioContent]:
        """Execute a tool by name with error handling"""
        try:
            handler = self.get_handler(name)
            if not handler:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

            return await handler.execute(arguments)

        except Exception as e:
            logger.error(f"Error in tool call {name}: {e}")
            return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


# Global tool registry instance
tool_registry = ToolRegistry()
