"""
MCP Terminal - A powerful terminal-based Model Context Protocol client

This package provides both direct tool execution capabilities and interactive
chat mode with LLM integration for MCP (Model Context Protocol) servers.
"""

from .core import MCPClient, MCPServerConfig, TransportType, MCPTool, MCPClientError
from .cli import main
from .chat import ChatSession
from .config import ConfigManager

__version__ = "1.0.0"
__author__ = "MCP Terminal"
__description__ = "A powerful terminal-based Model Context Protocol client"

__all__ = [
    "MCPClient",
    "MCPServerConfig", 
    "TransportType",
    "MCPTool",
    "MCPClientError",
    "ChatSession",
    "ConfigManager",
    "main"
] 