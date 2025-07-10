"""
MCP Shell CLI Interface

Command-line interface for the MCP Shell client that provides
both direct tool execution and interactive chat capabilities.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from .core import MCPClient, MCPServerConfig, TransportType, MCPClientError
from .chat import ChatSession
from .config import ConfigManager

console = Console()


class MCPTerminal:
    """Main MCP Shell application"""
    
    def __init__(self):
        self.client = MCPClient()
        self.config_manager = ConfigManager()
        self.chat_session: Optional[ChatSession] = None
    
    async def setup_servers_from_config(self):
        """Setup servers from configuration file"""
        configs = self.config_manager.load_servers()
        
        if not configs:
            console.print("[yellow]No servers configured. Use 'mcp-terminal server add' to add servers.[/yellow]")
            return
        
        for config in configs:
            await self.client.add_server(config)
    
    async def add_server_interactive(self):
        """Interactively add a new server"""
        console.print("[bold cyan]🔧 Add New MCP Server[/bold cyan]\n")
        
        # Get server name using standard input to avoid Rich interference
        console.print("[cyan]Server name:[/cyan]", end=" ")
        name = input().strip()
        
        # Get transport type
        while True:
            console.print("[cyan]Transport type [stdio/http] (stdio):[/cyan]", end=" ")
            transport_input = input().strip()
            transport_choice = transport_input if transport_input else "stdio"
            
            if transport_choice.lower() in ["stdio", "http"]:
                break
            else:
                console.print(f"[red]❌ Invalid transport type '{transport_choice}'. Please enter 'stdio' or 'http'.[/red]")
        
        transport = TransportType.STDIO if transport_choice == "stdio" else TransportType.HTTP
        
        config = None
        if transport == TransportType.STDIO:
            # stdio server configuration
            console.print("[cyan]Command to run server:[/cyan]", end=" ")
            command = input().strip()
            
            console.print("[cyan]Arguments (space-separated):[/cyan]", end=" ")
            args_input = input().strip()
            args = args_input.split() if args_input else []
            
            config = MCPServerConfig(
                name=name,
                transport=transport,
                command=command,
                args=args
            )
        else:
            # HTTP server configuration
            console.print("[cyan]Server URL (http://localhost:8000/mcp):[/cyan]", end=" ")
            url_input = input().strip()
            url = url_input if url_input else "http://localhost:8000/mcp"
            
            config = MCPServerConfig(
                name=name,
                transport=transport,
                url=url
            )
        
        # Now that we have clean input, proceed with connection
        console.print(f"\n[cyan]🔌 Connecting to server: {name}[/cyan]")
        
        # Save to config first
        self.config_manager.add_server(config)
        
        # Test the connection
        success = await self.client.add_server(config)
        
        if success:
            console.print(f"[green]✅ Server '{name}' added successfully![/green]")
        else:
            console.print(f"[red]❌ Failed to connect to server '{name}'[/red]")
            # Remove from config if connection failed
            self.config_manager.remove_server(name)
    
    async def remove_server(self, name: str, force: bool = False):
        """Remove a server"""
        # Check if server exists first
        server_config = self.config_manager.get_server(name)
        if not server_config:
            console.print(f"[red]❌ Server '{name}' not found in configuration[/red]")
            
            # Show available servers
            configs = self.config_manager.load_servers()
            if configs:
                console.print("\n[yellow]Available servers:[/yellow]")
                for config in configs:
                    console.print(f"  • {config.name}")
            else:
                console.print("[dim]No servers configured.[/dim]")
            return
        
        # Show server details
        console.print(f"[yellow]Server to remove:[/yellow]")
        if server_config.transport == TransportType.STDIO:
            details = f"{server_config.command} {' '.join(server_config.args or [])}"
        else:
            details = server_config.url or "No URL"
        console.print(f"  Name: {server_config.name}")
        console.print(f"  Transport: {server_config.transport.value}")
        console.print(f"  Details: {details}")
        
        # Confirmation (unless forced)
        if not force:
            console.print()
            confirm = Prompt.ask(
                f"[red]Are you sure you want to remove server '{name}'?[/red]",
                choices=["y", "n"],
                default="n"
            )
            if confirm.lower() != "y":
                console.print("[yellow]❌ Server removal cancelled[/yellow]")
                return
        
        # Remove the server
        success = self.config_manager.remove_server(name)
        if success:
            console.print(f"[green]✅ Server '{name}' removed from configuration[/green]")
        else:
            console.print(f"[red]❌ Failed to remove server '{name}'[/red]")
    
    def list_servers(self):
        """List configured servers"""
        configs = self.config_manager.load_servers()
        
        if not configs:
            console.print("[yellow]No servers configured.[/yellow]")
            return
        
        table = Table(title="📋 Configured MCP Servers")
        table.add_column("Name", style="cyan")
        table.add_column("Transport", style="green")
        table.add_column("Details", style="yellow")
        
        for config in configs:
            if config.transport == TransportType.STDIO:
                details = f"{config.command} {' '.join(config.args or [])}"
            else:
                details = config.url or "No URL"
            
            table.add_row(config.name, config.transport.value, details)
        
        console.print(table)
    
    async def show_model_selection_menu(self) -> Optional[str]:
        """Show interactive model selection menu"""
        console.print("[bold cyan]🚀 Select a model:[/bold cyan]\n")
        
        # Predefined popular models
        popular_models = [
            ("gpt-4o", "OpenAI GPT-4o (Latest GPT)"),
            ("gpt-4o-mini", "OpenAI GPT-4o Mini (Fast & Cheap)"),
            ("claude-3-5-sonnet-20241022", "Anthropic Claude 3.5 Sonnet (Latest)"),
            ("claude-3-haiku-20240307", "Anthropic Claude 3 Haiku (Fast)"),
            ("gemini-1.5-flash", "Google Gemini 1.5 Flash"),
            ("groq/llama-3.1-70b-versatile", "Groq Llama 3.1 70B"),
        ]
        
        # Get Ollama models if available
        ollama_models = []
        if self.client.is_ollama_available():
            models = await self.client.get_ollama_models()
            ollama_models = [(f"ollama/{m['name']}", f"Ollama: {m['name']} (Local)") for m in models]
        
        # Build options menu
        options = []
        
        # Add popular cloud models
        console.print("[bold]⭐ Popular Models:[/bold]")
        for i, (model, desc) in enumerate(popular_models, 1):
            console.print(f"   {i}. {desc}")
            options.append(model)
        
        # Add Ollama models if available
        if ollama_models:
            console.print(f"\n[bold]🦙 Local Ollama Models:[/bold]")
            for i, (model, desc) in enumerate(ollama_models, len(popular_models) + 1):
                console.print(f"   {i}. {desc}")
                options.append(model)
        else:
            console.print(f"\n[dim]🦙 No Ollama models found (install Ollama and pull models to see them here)[/dim]")
        
        # Add special options
        browse_option = len(options) + 1
        manual_option = len(options) + 2
        console.print(f"\n   {browse_option}. 🔍 Browse all available models")
        console.print(f"   {manual_option}. ✏️  Enter model name manually")
        console.print(f"   0. ❌ Cancel")
        
        # Get user choice
        try:
            choice = int(Prompt.ask(
                "\n🎯 Enter your choice",
                default="2"  # Default to gpt-4o-mini
            ))
            
            if choice == 0:
                return None
            elif 1 <= choice <= len(options):
                return options[choice - 1]
            elif choice == browse_option:
                return await self._browse_all_models()
            elif choice == manual_option:
                return self._manual_model_entry()
            else:
                console.print("[red]❌ Invalid choice[/red]")
                return None
                
        except (ValueError, KeyboardInterrupt):
            console.print("[yellow]❌ Selection cancelled[/yellow]")
            return None
    
    async def _browse_all_models(self) -> Optional[str]:
        """Browse all available models by provider"""
        console.print("\n[bold cyan]🔍 Browse Models by Provider[/bold cyan]\n")
        
        providers = [
            ("OpenAI", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]),
            ("Anthropic", ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]),
            ("Google", ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]),
            ("Groq", ["groq/llama-3.1-70b-versatile", "groq/llama-3.1-8b-instant", "groq/mixtral-8x7b-32768"]),
        ]
        
        # Add Ollama if available
        if self.client.is_ollama_available():
            models = await self.client.get_ollama_models()
            if models:
                ollama_models = [f"ollama/{m['name']}" for m in models]
                providers.append(("Ollama (Local)", ollama_models))
        
        # Show providers
        for i, (provider, models) in enumerate(providers, 1):
            console.print(f"   {i}. {provider} ({len(models)} models)")
        
        console.print(f"   0. ← Go back")
        
        try:
            choice = int(Prompt.ask("\n🎯 Select provider"))
            
            if choice == 0:
                return await self.show_model_selection_menu()
            elif 1 <= choice <= len(providers):
                provider_name, models = providers[choice - 1]
                return self._select_from_provider(provider_name, models)
            else:
                console.print("[red]❌ Invalid choice[/red]")
                return None
                
        except (ValueError, KeyboardInterrupt):
            return None
    
    def _select_from_provider(self, provider_name: str, models: List[str]) -> Optional[str]:
        """Select a model from a specific provider"""
        console.print(f"\n[bold cyan]🔍 {provider_name} Models[/bold cyan]\n")
        
        for i, model in enumerate(models, 1):
            # Clean up model name for display
            display_name = model.replace("groq/", "").replace("ollama/", "")
            console.print(f"   {i}. {display_name}")
        
        console.print(f"   0. ← Go back")
        
        try:
            choice = int(Prompt.ask("\n🎯 Select model"))
            
            if choice == 0:
                return None
            elif 1 <= choice <= len(models):
                return models[choice - 1]
            else:
                console.print("[red]❌ Invalid choice[/red]")
                return None
                
        except (ValueError, KeyboardInterrupt):
            return None
    
    def _manual_model_entry(self) -> Optional[str]:
        """Allow manual model entry"""
        console.print("\n[bold cyan]✏️  Manual Model Entry[/bold cyan]")
        console.print("[dim]Examples: gpt-4o, claude-3-5-sonnet-20241022, ollama/llama3.2, groq/llama-3.1-70b-versatile[/dim]\n")
        
        try:
            model = Prompt.ask("Enter model name")
            if model.strip():
                return model.strip()
            return None
        except KeyboardInterrupt:
            return None
    
    async def pull_ollama_model(self, model_name: str):
        """Pull an Ollama model interactively"""
        if not self.client.is_ollama_available():
            console.print("[red]❌ Ollama is not available[/red]")
            console.print("[dim]   Install from: https://ollama.com[/dim]")
            return
        
        success = await self.client.pull_ollama_model(model_name)
        if success:
            console.print(f"[green]✅ Model '{model_name}' is now available for local use[/green]")
        else:
            console.print(f"[red]❌ Failed to pull model '{model_name}'[/red]")
    
    async def call_tool_with_args(self, tool_name: str, **kwargs):
        """Call a tool with provided arguments"""
        try:
            # Remove None values and convert to proper types
            arguments = {k: v for k, v in kwargs.items() if v is not None}
            
            # Show what we're calling
            console.print(f"[cyan]🛠️  Calling tool: [bold]{tool_name}[/bold][/cyan]")
            if arguments:
                console.print(f"[dim]Arguments: {arguments}[/dim]")
            
            # Call the tool
            result = await self.client.call_tool(tool_name, arguments)
            
            # Display result
            self._display_tool_result(tool_name, result)
            
        except MCPClientError as e:
            console.print(f"[red]❌ {e}[/red]")
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")
    
    def _display_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """Display tool execution result"""
        content_items = result.get("content", [])
        
        if not content_items:
            console.print("[yellow]Tool executed but returned no content[/yellow]")
            return
        
        for item in content_items:
            content_type = item.get("type", "text")
            
            if content_type == "text":
                text_content = item.get("text", "")
                console.print(Panel(
                    text_content,
                    title=f"🔧 {tool_name} Result",
                    border_style="green"
                ))
            elif content_type == "resource":
                # Handle resource content
                resource_info = f"Resource: {item.get('resource', {}).get('uri', 'Unknown')}"
                console.print(Panel(
                    resource_info,
                    title=f"📄 {tool_name} Resource",
                    border_style="blue"
                ))
            else:
                # Handle other content types
                console.print(Panel(
                    json.dumps(item, indent=2),
                    title=f"📊 {tool_name} Data",
                    border_style="yellow"
                ))
    
    async def start_chat_mode(self, model: str = "gpt-4.1", api_key: Optional[str] = None):
        """Start interactive chat mode"""
        try:
            # Ensure we have servers connected
            if not self.client.tools:
                console.print("[yellow]⚠️  No MCP tools available. Connecting to configured servers...[/yellow]")
                await self.setup_servers_from_config()
            
            # Create chat session
            self.chat_session = ChatSession(
                mcp_client=self.client,
                model=model,
                api_key=api_key
            )
            
            # Start chat
            await self.chat_session.start_interactive()
            
        except Exception as e:
            console.print(f"[red]❌ Failed to start chat mode: {e}[/red]")
            sys.exit(1)
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.close()
        if self.chat_session:
            await self.chat_session.close()


# Global instance
app = MCPTerminal()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
def cli(ctx, config):
    """🚀 MCP Shell - A powerful shell-based Model Context Protocol client
    
    Connect to MCP servers and execute tools directly from the command line,
    or start an interactive chat session with LLM integration.
    """
    logo = (
        "    +=========================================+\n"
        "    |                                         |\n"
        "    |  ███╗   ███╗ ██████╗██████╗             |\n"
        "    |  ████╗ ████║██╔════╝██╔══██╗            |\n"
        "    |  ██╔████╔██║██║     ██████╔╝            |\n"
        "    |  ██║╚██╔╝██║██║     ██╔═══╝             |\n"
        "    |  ██║ ╚═╝ ██║╚██████╗██║                 |\n"
        "    |  ╚═╝     ╚═╝ ╚═════╝╚═╝                 |\n"
        "    |                                         |\n"
        "    | ███████╗██╗  ██╗███████╗██╗     ██╗     |\n"
        "    | ██╔════╝██║  ██║██╔════╝██║     ██║     |\n"
        "    | ███████╗███████║█████╗  ██║     ██║     |\n"
        "    | ╚════██║██╔══██║██╔══╝  ██║     ██║     |\n"
        "    | ███████║██║  ██║███████╗███████╗███████╗|\n"
        "    | ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝|\n"
        "    |                                         |\n"
        "    +=========================================+"
    )

    if config:
        app.config_manager.config_path = Path(config)
    
    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        console.print(logo)
        click.echo(ctx.get_help())
        
        # Also show available tools if any servers are configured
        async def _show_tools():
            try:
                await app.setup_servers_from_config()
                if app.client.tools:
                    console.print("\n")
                    app.client.show_tools()
                    console.print("\n[dim]💡 Use 'mcp-terminal tool <tool_name> --help' to see tool usage[/dim]")
            except Exception:
                pass  # Silently fail if can't connect
            finally:
                await app.cleanup()
        
        try:
            asyncio.run(_show_tools())
        except Exception:
            pass


@cli.group()
def server():
    """Manage MCP servers"""
    pass


@server.command('add')
def server_add():
    """Add a new MCP server interactively"""
    async def _run_add():
        try:
            await app.add_server_interactive()
        finally:
            await app.cleanup()
    
    asyncio.run(_run_add())


@server.command('remove')
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Remove server without confirmation')
def server_remove(name, force):
    """Remove an MCP server"""
    async def _run_remove():
        try:
            await app.remove_server(name, force=force)
        finally:
            await app.cleanup()
    
    asyncio.run(_run_remove())


@server.command('list')
def server_list():
    """List configured MCP servers"""
    app.list_servers()


@server.command('status')
def server_status():
    """Show server connection status"""
    async def _run_status():
        try:
            await app.setup_servers_from_config()
            app.client.show_status()
        finally:
            await app.cleanup()
    
    asyncio.run(_run_status())


@cli.command()
def tools():
    """List available MCP tools"""
    async def _run_tools():
        try:
            await app.setup_servers_from_config()
            app.client.show_tools()
        finally:
            await app.cleanup()
    
    asyncio.run(_run_tools())


@cli.command()
@click.argument('tool_name')
def tool_help(tool_name):
    """Show detailed help for a specific tool"""
    async def _run_tool_help():
        try:
            await app.setup_servers_from_config()
            app.client.show_tool_help(tool_name)
        finally:
            await app.cleanup()
    
    asyncio.run(_run_tool_help())


@cli.command()
@click.argument('tool_name')
@click.option('--server', help='Specify server if tool exists on multiple servers')
@click.pass_context
def tool(ctx, tool_name, server):
    """
    Execute an MCP tool
    
    TOOL_NAME: Name of the tool to execute
    
    Additional arguments depend on the specific tool.
    Use 'mcp-terminal tool-help <tool_name>' to see available parameters.
    """
    
    async def _run_tool():
        try:
            # Setup servers first
            await app.setup_servers_from_config()
            
            # Get the tool to understand its parameters
            full_tool_name = f"{server}:{tool_name}" if server else tool_name
            tool_obj = app.client.get_tool(full_tool_name)
            
            if not tool_obj:
                console.print(f"[red]❌ Tool '{tool_name}' not found[/red]")
                available_tools = [t.name for t in app.client.list_tools()]
                if available_tools:
                    console.print(f"[dim]Available tools: {', '.join(available_tools)}[/dim]")
                return
            
            # For now, we'll collect arguments interactively if none provided
            # In a future version, we could parse click options dynamically
            arguments = {}
            
            if tool_obj.parameters.get("properties"):
                console.print(f"[cyan]🔧 Executing tool: [bold]{tool_name}[/bold][/cyan]")
                console.print(f"[dim]{tool_obj.description}[/dim]\n")
                
                props = tool_obj.parameters["properties"]
                required = tool_obj.parameters.get("required", [])
                
                for param_name, param_info in props.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "No description")
                    is_required = param_name in required
                    
                    # Build prompt
                    prompt_text = f"{param_name}"
                    if is_required:
                        prompt_text += " (required)"
                    prompt_text += f" [{param_type}]"
                    
                    console.print(f"[yellow]{param_desc}[/yellow]")
                    
                    if is_required:
                        value = Prompt.ask(prompt_text)
                    else:
                        value = Prompt.ask(prompt_text, default="")
                    
                    if value.strip():
                        # Convert to appropriate type
                        if param_type == "integer":
                            try:
                                arguments[param_name] = int(value)
                            except ValueError:
                                console.print(f"[red]❌ Invalid integer value for {param_name}[/red]")
                                return
                        elif param_type == "number":
                            try:
                                arguments[param_name] = float(value)
                            except ValueError:
                                console.print(f"[red]❌ Invalid number value for {param_name}[/red]")
                                return
                        elif param_type == "boolean":
                            arguments[param_name] = value.lower() in ("true", "yes", "y", "1")
                        else:
                            arguments[param_name] = value
                    
                    console.print()  # Empty line for readability
            
            # Execute the tool
            await app.call_tool_with_args(full_tool_name, **arguments)
        finally:
            await app.cleanup()
    
    asyncio.run(_run_tool())


@cli.command()
@click.option('--model', '-m', default='gpt-4.1', help='LLM model to use')
@click.option('--api-key', help='API key for LLM (or set via environment)')
def chat(model, api_key):
    """Start interactive chat mode with MCP integration"""
    async def _run_chat():
        try:
            await app.start_chat_mode(model=model, api_key=api_key)
        finally:
            await app.cleanup()
    
    asyncio.run(_run_chat())


@cli.command()
@click.argument('query')
@click.option('--model', '-m', default='gpt-4.1', help='LLM model to use')
@click.option('--api-key', help='API key for LLM (or set via environment)')
def ask(query, model, api_key):
    """Ask a single question in chat mode"""
    
    async def _run_ask():
        try:
            await app.setup_servers_from_config()
            
            chat_session = ChatSession(
                mcp_client=app.client,
                model=model,
                api_key=api_key
            )
            
            await chat_session.process_message(query)
            await chat_session.close()
            
        except Exception as e:
            console.print(f"[red]❌ Error processing query: {e}[/red]")
        finally:
            await app.cleanup()
    
    asyncio.run(_run_ask())


def main():
    """Main entry point"""
    # Run the CLI
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            asyncio.run(app.cleanup())
        except Exception:
            pass  # Ignore cleanup errors


if __name__ == '__main__':
    main() 