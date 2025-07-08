"""
Core MCP Shell Client Implementation

A modern, clean implementation of a Model Context Protocol (MCP) client
that provides both direct tool execution and interactive chat capabilities.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax

console = Console()


class TransportType(Enum):
    """Supported MCP transport types"""
    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection"""
    name: str
    transport: TransportType
    
    # For stdio servers
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    
    # For HTTP/SSE servers
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    description: Optional[str] = None
    timeout: int = 30


@dataclass 
class MCPTool:
    """Represents an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_name: str
    
    def get_parameter_info(self) -> str:
        """Get formatted parameter information"""
        if not self.parameters.get("properties"):
            return "No parameters"
        
        props = self.parameters["properties"]
        required = self.parameters.get("required", [])
        
        info = []
        for param, details in props.items():
            req_str = " (required)" if param in required else " (optional)"
            param_type = details.get("type", "unknown")
            desc = details.get("description", "No description")
            info.append(f"  --{param} ({param_type}){req_str}: {desc}")
        
        return "\n".join(info)


@dataclass
class MCPResponse:
    """MCP JSON-RPC response"""
    id: Optional[str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
    @property
    def is_success(self) -> bool:
        return self.error is None
    
    @property
    def error_message(self) -> str:
        if self.error:
            return self.error.get("message", "Unknown error")
        return ""


class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPClient:
    """
    Core MCP client implementation
    
    Handles JSON-RPC communication with MCP servers via multiple transports
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.connections: Dict[str, Any] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.next_id = 1
    
    def get_next_id(self) -> str:
        """Get next request ID"""
        current_id = str(self.next_id)
        self.next_id += 1
        return current_id
    
    async def add_server(self, config: MCPServerConfig) -> bool:
        """Add and connect to an MCP server"""
        try:
            console.print(f"🔌 Connecting to server: [bold]{config.name}[/bold]")
            
            if config.transport == TransportType.STDIO:
                success = await self._connect_stdio_server(config)
            elif config.transport == TransportType.HTTP:
                success = await self._connect_http_server(config)
            else:
                console.print(f"[red]❌ Unsupported transport: {config.transport}[/red]")
                return False
            
            if success:
                self.servers[config.name] = config
                await self._load_server_tools(config.name)
                console.print(f"[green]✅ Connected to {config.name}[/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to connect to {config.name}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error connecting to {config.name}: {e}[/red]")
            return False
    
    async def _connect_stdio_server(self, config: MCPServerConfig) -> bool:
        """Connect to stdio-based MCP server"""
        if not config.command:
            raise MCPClientError("stdio servers require a command")
        
        try:
            cmd = [config.command] + (config.args or [])
            env = config.env or {}
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=config.cwd
            )
            
            # Initialize the connection
            init_response = await self._send_request_stdio(
                process,
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-terminal",
                        "version": "1.0.0"
                    }
                }
            )
            
            if init_response.is_success:
                self.connections[config.name] = process
                return True
            
            return False
            
        except Exception as e:
            console.print(f"[red]Error in stdio connection: {e}[/red]")
            return False
    
    async def _connect_http_server(self, config: MCPServerConfig) -> bool:
        """Connect to HTTP-based MCP server"""
        if not config.url:
            raise MCPClientError("HTTP servers require a URL")
        
        try:
            # Set up headers to accept both JSON and SSE
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }
            if config.headers:
                headers.update(config.headers)
            
            session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            )
            
            # Test connection and initialize
            init_response = await self._send_request_http(
                session,
                config.url,
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-terminal",
                        "version": "1.0.0"
                    }
                }
            )
            
            if init_response.is_success:
                self.connections[config.name] = session
                return True
            else:
                await session.close()
                return False
                
        except Exception as e:
            console.print(f"[red]Error in HTTP connection: {e}[/red]")
            # Try to close session if it was created
            try:
                if 'session' in locals():
                    await session.close()
            except:
                pass
            return False
    
    async def _send_request_stdio(self, process, method: str, params: Dict[str, Any]) -> MCPResponse:
        """Send JSON-RPC request via stdio"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method,
            "params": params
        }
        
        request_line = json.dumps(request) + "\n"
        process.stdin.write(request_line.encode())
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        if not response_line:
            return MCPResponse(id=request["id"], error={"message": "No response from server"})
        
        try:
            response_data = json.loads(response_line.decode().strip())
            return MCPResponse(
                id=response_data.get("id"),
                result=response_data.get("result"),
                error=response_data.get("error")
            )
        except json.JSONDecodeError as e:
            return MCPResponse(id=request["id"], error={"message": f"Invalid JSON response: {e}"})
    
    async def _send_request_http(self, session: aiohttp.ClientSession, url: str, 
                                method: str, params: Dict[str, Any]) -> MCPResponse:
        """Send JSON-RPC request via HTTP"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method,
            "params": params
        }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            async with session.post(url, json=request, headers=headers) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'text/event-stream' in content_type:
                        # Handle SSE response
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                data = line[6:]  # Remove 'data: ' prefix
                                if data and data != '[DONE]':
                                    try:
                                        response_data = json.loads(data)
                                        return MCPResponse(
                                            id=response_data.get("id"),
                                            result=response_data.get("result"),
                                            error=response_data.get("error")
                                        )
                                    except json.JSONDecodeError:
                                        continue
                        
                        return MCPResponse(
                            id=request["id"], 
                            error={"message": "No valid JSON data found in SSE stream"}
                        )
                    
                    else:
                        # Handle regular JSON response
                        response_text = await response.text()
                        
                        try:
                            response_data = json.loads(response_text)
                            return MCPResponse(
                                id=response_data.get("id"),
                                result=response_data.get("result"),
                                error=response_data.get("error")
                            )
                        except json.JSONDecodeError as e:
                            return MCPResponse(
                                id=request["id"], 
                                error={"message": f"Invalid JSON response: {e}. Response: {response_text[:100]}"}
                            )
                else:
                    error_text = await response.text()
                    return MCPResponse(
                        id=request["id"], 
                        error={"message": f"HTTP {response.status}: {error_text[:100]}"}
                    )
        except Exception as e:
            return MCPResponse(id=request["id"], error={"message": f"HTTP request failed: {e}"})
    
    async def _load_server_tools(self, server_name: str):
        """Load available tools from a server"""
        try:
            config = self.servers[server_name]
            connection = self.connections[server_name]
            
            if config.transport == TransportType.STDIO:
                response = await self._send_request_stdio(connection, "tools/list", {})
            else:
                response = await self._send_request_http(connection, config.url, "tools/list", {})
            
            if response.is_success and response.result:
                tools_data = response.result.get("tools", [])
                for tool_data in tools_data:
                    tool_name = tool_data["name"]
                    # Create unique tool name to avoid conflicts
                    unique_name = f"{server_name}:{tool_name}"
                    
                    self.tools[unique_name] = MCPTool(
                        name=tool_name,
                        description=tool_data.get("description", "No description"),
                        parameters=tool_data.get("inputSchema", {}),
                        server_name=server_name
                    )
            
        except Exception as e:
            console.print(f"[red]Failed to load tools from {server_name}: {e}[/red]")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        # Handle both full names (server:tool) and short names
        if ":" in tool_name:
            server_name, actual_tool_name = tool_name.split(":", 1)
            full_tool_name = tool_name
        else:
            # Find tool by short name
            matching_tools = [name for name in self.tools.keys() if name.endswith(f":{tool_name}")]
            if not matching_tools:
                raise MCPClientError(f"Tool '{tool_name}' not found")
            if len(matching_tools) > 1:
                server_names = [name.split(":")[0] for name in matching_tools]
                raise MCPClientError(
                    f"Tool '{tool_name}' found on multiple servers: {', '.join(server_names)}. "
                    f"Use format 'server:tool' to specify."
                )
            full_tool_name = matching_tools[0]
            server_name, actual_tool_name = full_tool_name.split(":", 1)
        
        if full_tool_name not in self.tools:
            raise MCPClientError(f"Tool '{tool_name}' not found")
        
        config = self.servers[server_name]
        connection = self.connections[server_name]
        
        params = {
            "name": actual_tool_name,
            "arguments": arguments
        }
        
        try:
            if config.transport == TransportType.STDIO:
                response = await self._send_request_stdio(connection, "tools/call", params)
            else:
                response = await self._send_request_http(connection, config.url, "tools/call", params)
            
            if response.is_success:
                return response.result
            else:
                raise MCPClientError(f"Tool call failed: {response.error_message}")
                
        except Exception as e:
            raise MCPClientError(f"Failed to call tool {tool_name}: {e}")
    
    def list_tools(self) -> List[MCPTool]:
        """Get list of all available tools"""
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get tool by name"""
        if ":" in tool_name:
            return self.tools.get(tool_name)
        else:
            # Find by short name
            for full_name, tool in self.tools.items():
                if full_name.endswith(f":{tool_name}"):
                    return tool
            return None
    
    def show_status(self):
        """Display current client status"""
        table = Table(title="🔗 MCP Client Status")
        table.add_column("Server", style="cyan")
        table.add_column("Transport", style="green") 
        table.add_column("Tools", style="yellow")
        table.add_column("Status", style="blue")
        
        for server_name, config in self.servers.items():
            tool_count = len([t for t in self.tools.values() if t.server_name == server_name])
            status = "✅ Connected" if server_name in self.connections else "❌ Disconnected"
            
            table.add_row(
                server_name,
                config.transport.value,
                str(tool_count),
                status
            )
        
        console.print(table)
    
    def show_tools(self):
        """Display available tools"""
        if not self.tools:
            console.print("[yellow]No tools available. Connect to MCP servers first.[/yellow]")
            return
        
        table = Table(title="🛠️  Available MCP Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Server", style="green")
        table.add_column("Description", style="yellow")
        
        for full_name, tool in self.tools.items():
            table.add_row(
                tool.name,
                tool.server_name,
                tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
            )
        
        console.print(table)
    
    def show_tool_help(self, tool_name: str):
        """Show detailed help for a specific tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            console.print(f"[red]Tool '{tool_name}' not found[/red]")
            return
        
        panel_content = f"""[bold cyan]{tool.name}[/bold cyan]
[yellow]Server:[/yellow] {tool.server_name}

[yellow]Description:[/yellow]
{tool.description}

[yellow]Parameters:[/yellow]
{tool.get_parameter_info()}"""
        
        console.print(Panel(panel_content, title=f"Tool: {tool.name}", border_style="blue"))
    
    async def close(self):
        """Close all connections"""
        for server_name, connection in self.connections.items():
            try:
                config = self.servers[server_name]
                if config.transport == TransportType.STDIO:
                    # Terminate stdio process
                    connection.terminate()
                    await connection.wait()
                elif config.transport == TransportType.HTTP:
                    # Close HTTP session
                    await connection.close()
            except Exception as e:
                console.print(f"[red]Error closing connection to {server_name}: {e}[/red]")
        
        self.connections.clear()
        self.servers.clear()
        self.tools.clear() 