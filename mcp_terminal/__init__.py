"""
MCP Shell - A powerful shell-based Model Context Protocol client

This package provides both direct tool execution capabilities and interactive
chat mode with LLM integration for MCP (Model Context Protocol) servers.
"""

from .core import MCPClient, MCPServerConfig, TransportType, MCPTool, MCPClientError
from .cli import main
from .chat import ChatSession
from .character_chat import CharacterChatSession, HistoricalCharacter, Veo3VideoGenerator
from .config import ConfigManager

__version__ = "1.0.0"
__author__ = "MCP Shell"
__description__ = "A powerful shell-based Model Context Protocol client"

__all__ = [
    "MCPClient",
    "MCPServerConfig", 
    "TransportType",
    "MCPTool",
    "MCPClientError",
    "ChatSession",
    "CharacterChatSession",
    "HistoricalCharacter",
    "Veo3VideoGenerator",
    "ConfigManager",
    "main"
] 