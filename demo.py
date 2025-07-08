#!/usr/bin/env python3
"""
MCP Terminal Demo - Showcase of the terminal-based MCP client

This demo shows how to use the MCP Terminal client both
programmatically and via command line.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the package to path for development
sys.path.insert(0, str(Path(__file__).parent))

from mcp_terminal import MCPClient, MCPServerConfig, TransportType, ChatSession
from rich.console import Console
from rich.panel import Panel

console = Console()


async def demo_basic_client():
    """Demo basic MCP client functionality"""
    console.print("[bold cyan]🚀 MCP Terminal Demo - Basic Client[/bold cyan]\n")
    
    # Create client
    client = MCPClient()
    
    # Example server configuration (won't actually connect without real server)
    demo_config = MCPServerConfig(
        name="demo-server",
        transport=TransportType.STDIO,
        command="echo",  # Simple echo command for demo
        args=['{"result": {"tools": []}}'],  # Mock response
        description="Demo server for testing"
    )
    
    console.print("📋 Demo server configuration:")
    console.print(f"  Name: {demo_config.name}")
    console.print(f"  Transport: {demo_config.transport.value}")
    console.print(f"  Command: {demo_config.command}")
    console.print()
    
    # Show status (no servers connected)
    console.print("📊 Client status:")
    client.show_status()
    console.print()
    
    # Show tools (none available)
    console.print("🛠️  Available tools:")
    client.show_tools()
    console.print()
    
    await client.close()


async def demo_chat_session():
    """Demo chat session (without actual LLM)"""
    console.print("[bold cyan]🤖 MCP Terminal Demo - Chat Session[/bold cyan]\n")
    
    # Create a mock client
    client = MCPClient()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        console.print(f"[green]✅ API key found: {api_key[:10]}...[/green]")
        console.print("[yellow]💡 You can start interactive chat with: mcp-terminal chat[/yellow]")
    else:
        console.print("[yellow]⚠️  No API key found. Set one of:[/yellow]")
        console.print("   export OPENAI_API_KEY='your-key'")
        console.print("   export ANTHROPIC_API_KEY='your-key'")
        console.print("   export GOOGLE_API_KEY='your-key'")
    
    console.print()


def demo_cli_commands():
    """Show CLI command examples"""
    console.print("[bold cyan]⚡ MCP Terminal Demo - CLI Commands[/bold cyan]\n")
    
    commands = [
        ("mcp-terminal --help", "Show main help"),
        ("mcp-terminal server add", "Add a new MCP server interactively"),
        ("mcp-terminal server list", "List configured servers"),
        ("mcp-terminal server status", "Show server connection status"),
        ("mcp-terminal tools", "List available MCP tools"),
        ("mcp-terminal tool-help <tool_name>", "Get help for a specific tool"),
        ("mcp-terminal tool <tool_name>", "Execute a tool interactively"),
        ("mcp-terminal chat", "Start interactive chat mode"),
        ("mcp-terminal ask 'Your question'", "Ask a single question"),
    ]
    
    console.print("🔧 Available CLI commands:\n")
    for cmd, desc in commands:
        console.print(f"  [cyan]{cmd:<35}[/cyan] - {desc}")
    
    console.print()


def demo_server_examples():
    """Show MCP server examples"""
    console.print("[bold cyan]🌐 MCP Terminal Demo - Server Examples[/bold cyan]\n")
    
    servers = [
        {
            "name": "Filesystem Server",
            "install": "npm install -g @modelcontextprotocol/server-filesystem",
            "command": "npx @modelcontextprotocol/server-filesystem /tmp",
            "description": "Provides file system operations"
        },
        {
            "name": "Git Server", 
            "install": "pip install mcp-server-git",
            "command": "python -m mcp_server_git",
            "description": "Git repository management tools"
        },
        {
            "name": "Terminal Server",
            "install": "npm install -g @rinardnick/mcp-terminal",
            "command": "npx @rinardnick/mcp-terminal",
            "description": "Secure terminal command execution"
        },
        {
            "name": "Web Search Server",
            "install": "npm install -g @modelcontextprotocol/server-web-search", 
            "command": "npx @modelcontextprotocol/server-web-search",
            "description": "Web search and content fetching"
        }
    ]
    
    for server in servers:
        console.print(f"[bold yellow]{server['name']}[/bold yellow]")
        console.print(f"  Install: [green]{server['install']}[/green]")
        console.print(f"  Command: [cyan]{server['command']}[/cyan]")
        console.print(f"  Description: {server['description']}")
        console.print()


async def main():
    """Run the complete demo"""
    # Banner
    banner = """
[bold green]
╔══════════════════════════════════════════════════════════════════════════════════════╗
║     ██████╗ ███████╗███╗   ███╗ ██████╗     ███╗   ███╗ ██████╗ ██████╗ ███████╗     ║
║     ██╔══██╗██╔════╝████╗ ████║██╔═══██╗    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝     ║
║     ██║  ██║█████╗  ██╔████╔██║██║   ██║    ██╔████╔██║██║   ██║██║  ██║█████╗       ║
║     ██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║    ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝       ║
║     ██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗     ║
║     ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🚀 DEMO MODE 🚀

Welcome to the MCP Terminal demonstration!
This shows the capabilities of the modern terminal-based
Model Context Protocol client.
[/bold green]
    """
    
    console.print(Panel(banner.strip(), title="Demo", border_style="green"))
    console.print()
    
    # Run demos
    await demo_basic_client()
    await demo_chat_session()
    demo_cli_commands()
    demo_server_examples()
    
    # Final instructions
    console.print("[bold green]🎉 Demo Complete![/bold green]\n")
    
    console.print("[yellow]Next steps:[/yellow]")
    console.print("1. Install an MCP server (see examples above)")
    console.print("2. Add it with: [cyan]mcp-terminal server add[/cyan]")
    console.print("3. List tools with: [cyan]mcp-terminal tools[/cyan]")
    console.print("4. Start chatting with: [cyan]mcp-terminal chat[/cyan]")
    console.print()
    
    console.print("[dim]💡 For full documentation, see README.md[/dim]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Demo interrupted![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Demo error: {e}[/red]")
        sys.exit(1) 