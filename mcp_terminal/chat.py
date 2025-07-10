"""
Interactive Chat Session for MCP Shell

Provides LLM-powered chat with automatic MCP tool calling capabilities
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional

import litellm
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.markdown import Markdown
import textwrap

from .core import MCPClient, MCPClientError

console = Console()


class ChatSession:
    """
    Interactive chat session with LLM and MCP integration
    """
    
    def __init__(self, mcp_client: MCPClient, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.mcp_client = mcp_client
        self.model = model
        self.api_key = api_key or self._get_api_key()
        self.conversation_history: List[Dict[str, Any]] = []
        self.running = False
        self.is_ollama_model = self._is_ollama_model(model)
        
        # Configure LiteLLM based on model type
        self._configure_llm()
    
    def _is_ollama_model(self, model: str) -> bool:
        """Check if the model is an Ollama model"""
        return model.startswith("ollama/") or (
            not any(model.startswith(prefix) for prefix in ["gpt", "claude", "gemini", "groq"]) and
            self.mcp_client.is_ollama_available()
        )
    
    def _configure_llm(self):
        """Configure LiteLLM based on model type"""
        if self.is_ollama_model:
            # For Ollama models, ensure the model is formatted correctly for LiteLLM
            if not self.model.startswith("ollama/"):
                self.model = f"ollama/{self.model}"
            
            # Set Ollama base URL if needed
            ollama_base_url = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
            os.environ['OLLAMA_API_BASE'] = ollama_base_url
            
            console.print(f"[green]🦙 Using Ollama model: {self.model.replace('ollama/', '')}[/green]")
        else:
            # Configure API keys for cloud providers
            if self.api_key:
                if self.model.startswith("gpt"):
                    os.environ["OPENAI_API_KEY"] = self.api_key
                elif self.model.startswith("claude"):
                    os.environ["ANTHROPIC_API_KEY"] = self.api_key
                elif self.model.startswith("gemini"):
                    os.environ["GOOGLE_API_KEY"] = self.api_key
                elif self.model.startswith("groq"):
                    os.environ["GROQ_API_KEY"] = self.api_key
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables"""
        # Try different environment variables
        for env_var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"]:
            api_key = os.environ.get(env_var)
            if api_key:
                return api_key
        return None
    
    async def validate_model(self) -> bool:
        """Validate that the selected model is available"""
        if self.is_ollama_model:
            if not self.mcp_client.is_ollama_available():
                console.print("[red]❌ Ollama is not running. Please start Ollama:[/red]")
                console.print("[dim]   ollama serve[/dim]")
                return False
            
            # Check if the specific model is available
            model_name = self.model.replace("ollama/", "")
            models = await self.mcp_client.get_ollama_models()
            model_names = [m.get('name', '').split(':')[0] for m in models]
            
            if model_name not in model_names and model_name not in [m.get('name', '') for m in models]:
                console.print(f"[yellow]⚠️  Model '{model_name}' not found locally.[/yellow]")
                
                # Offer to pull the model
                should_pull = Prompt.ask(
                    f"Would you like to pull '{model_name}' now?",
                    choices=["y", "n"],
                    default="y"
                )
                
                if should_pull.lower() == "y":
                    success = await self.mcp_client.pull_ollama_model(model_name)
                    if not success:
                        console.print(f"[red]❌ Failed to pull model '{model_name}'[/red]")
                        return False
                else:
                    console.print("[yellow]❌ Cannot proceed without the model[/yellow]")
                    return False
        else:
            # For cloud models, check if API key is available
            if not self.api_key:
                console.print("[red]❌ No API key found for cloud models.[/red]")
                console.print("[dim]   Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY[/dim]")
                return False
        
        return True
    
    def _show_welcome_banner(self):
        """Display welcome banner for chat mode"""
        banner_text = f"""[bold cyan]
+-------------------------------------------------------------------------------------+
|   ██████╗██╗  ██╗ █████╗ ████████╗    ███╗   ███╗ ██████╗ ██████╗ ███████╗            |
|  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝    ████╗ ████║██╔═══██╗██╔══██╗██╔════╝            |
|  ██║     ███████║███████║   ██║       ██╔████╔██║██║   ██║██║  ██║█████╗              |
|  ██║     ██╔══██║██╔══██║   ██║       ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝              |
|  ╚██████╗██║  ██║██║  ██║   ██║       ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗            |
|   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝            |
+-------------------------------------------------------------------------------------+

🤖 MCP Shell Chat Mode

Welcome to interactive chat with MCP tool integration!
Type your questions and I'll help you using available MCP tools.

Current Model: {self.model}{"" if not self.is_ollama_model else " (Local via Ollama)"}

Commands:
  /help     - Show this help
  /tools    - List available MCP tools  
  /status   - Show server connection status
  /model    - Show current model
  /models   - List available models
  /clear    - Clear conversation history
  /exit     - Exit chat mode
[/bold cyan]"""
        
        # Create a Text object from markup and disable wrapping
        text = Text.from_markup(textwrap.dedent(banner_text).strip())
        text.no_wrap = True

        console.print(Panel(text, title="Chat Session", border_style="blue"))
        
        # Show tool availability and limitations
        if self.mcp_client.tools:
            tool_count = len(self.mcp_client.tools)
            if self.is_ollama_model:
                console.print(f"[yellow]📦 {tool_count} MCP tools available, but this Ollama model doesn't support automatic tool calling.[/yellow]")
                console.print(f"[yellow]💡 You can ask about the tools and I'll guide you on how to use them manually.[/yellow]\n")
            else:
                console.print(f"[green]📦 {tool_count} MCP tools available for automatic use[/green]\n")
        else:
            console.print("[yellow]⚠️  No MCP tools available. Connect to servers first.[/yellow]\n")
    
    def _get_available_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function calling format"""
        tools = []
        
        for tool_name, tool in self.mcp_client.tools.items():
            # Convert MCP tool schema to OpenAI function format
            function_def = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            
            # Add server info to description for disambiguation
            if ":" in tool_name:
                server_name = tool_name.split(":")[0]
                function_def["description"] += f" (from {server_name} server)"
            
            tools.append({
                "type": "function",
                "function": function_def
            })
        
        return tools
    
    async def process_message(self, user_message: str):
        """Process a user message and generate response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare system message
        system_message = {
            "role": "system",
            "content": self._get_system_prompt()
        }
        
        # Prepare messages for LLM
        messages = [system_message] + self.conversation_history
        
        # Get available tools
        available_tools = self._get_available_tools_for_llm()
        
        try:
            # Show thinking indicator
            thinking_text = f"🤔 Thinking{'...' if not self.is_ollama_model else ' (local model)...'}"
            with Live(Spinner("dots", text=thinking_text), console=console, transient=True):
                
                # For Ollama models, disable function calling as many don't support it properly
                # Use text-based tool descriptions instead
                if available_tools and not self.is_ollama_model:
                    response = await asyncio.to_thread(
                        litellm.completion,
                        model=self.model,
                        messages=messages,
                        tools=available_tools,
                        tool_choice="auto",
                        temperature=0.7  # Add some creativity
                    )
                else:
                    # For Ollama models or when no tools, use regular completion
                    response = await asyncio.to_thread(
                        litellm.completion,
                        model=self.model,
                        messages=messages,
                        temperature=0.7
                    )
            
            message = response.choices[0].message
            
            # Handle tool calls (only for non-Ollama models)
            if hasattr(message, 'tool_calls') and message.tool_calls and not self.is_ollama_model:
                await self._handle_tool_calls(message, message.tool_calls)
            else:
                # Regular response
                assistant_content = message.content
                if assistant_content:
                    self._display_assistant_message(assistant_content)
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_content
                    })
        
        except Exception as e:
            error_msg = f"❌ Error generating response: {e}"
            if self.is_ollama_model and "Connection refused" in str(e):
                error_msg += "\n💡 Is Ollama running? Try: ollama serve"
            elif "API key" in str(e):
                error_msg += "\n💡 Check your API key configuration"
            elif self.is_ollama_model and "function" in str(e).lower():
                error_msg += "\n💡 Function calling not supported with this Ollama model"
            console.print(f"[red]{error_msg}[/red]")
    
    async def _handle_tool_calls(self, message, tool_calls):
        """Handle tool calling from LLM"""
        # Add the assistant message with tool calls to history
        self.conversation_history.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                } for call in tool_calls
            ]
        })
        
        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}
            
            console.print(f"[cyan]🔧 Calling tool: [bold]{function_name}[/bold][/cyan]")
            console.print(f"[dim]Arguments: {arguments}[/dim]")
            
            try:
                # Find the full tool name (with server prefix)
                full_tool_name = None
                for tool_key in self.mcp_client.tools.keys():
                    if tool_key.endswith(f":{function_name}"):
                        full_tool_name = tool_key
                        break
                
                if not full_tool_name:
                    result_content = f"Error: Tool '{function_name}' not found"
                else:
                    # Call the MCP tool
                    result = await self.mcp_client.call_tool(full_tool_name, arguments)
                    
                    # Format result for display and LLM
                    if result.get("content"):
                        result_content = self._format_tool_result(result)
                        self._display_tool_result(function_name, result)
                    else:
                        result_content = "Tool executed successfully (no output)"
                
                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_content
                })
                
            except Exception as e:
                error_msg = f"Tool execution failed: {e}"
                console.print(f"[red]❌ {error_msg}[/red]")
                
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": error_msg
                })
        
        # Get follow-up response from LLM after tool execution
        try:
            system_message = {
                "role": "system",
                "content": self._get_system_prompt()
            }
            messages = [system_message] + self.conversation_history
            
            with Live(Spinner("dots", text="🤔 Processing results..."), console=console, transient=True):
                response = await asyncio.to_thread(
                    litellm.completion,
                    model=self.model,
                    messages=messages
                )
            
            assistant_content = response.choices[0].message.content
            if assistant_content:
                self._display_assistant_message(assistant_content)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content
                })
        
        except Exception as e:
            console.print(f"[red]❌ Error getting follow-up response: {e}[/red]")
    
    def _format_tool_result(self, result: Dict[str, Any]) -> str:
        """Format tool result for LLM consumption"""
        content_items = result.get("content", [])
        
        if not content_items:
            return "No content returned"
        
        formatted_parts = []
        for item in content_items:
            content_type = item.get("type", "text")
            
            if content_type == "text":
                formatted_parts.append(item.get("text", ""))
            elif content_type == "resource":
                resource_info = item.get("resource", {})
                formatted_parts.append(f"Resource: {resource_info.get('uri', 'Unknown')}")
            else:
                formatted_parts.append(json.dumps(item, indent=2))
        
        return "\n".join(formatted_parts)
    
    def _display_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """Display tool result to user"""
        content_items = result.get("content", [])
        
        for item in content_items:
            content_type = item.get("type", "text")
            
            if content_type == "text":
                text_content = item.get("text", "")
                console.print(Panel(
                    text_content,
                    title=f"🔧 {tool_name}",
                    border_style="green"
                ))
            elif content_type == "resource":
                resource_info = item.get("resource", {})
                console.print(Panel(
                    f"Resource: {resource_info.get('uri', 'Unknown')}",
                    title=f"📄 {tool_name} Resource",
                    border_style="blue"
                ))
    
    def _display_assistant_message(self, content: str):
        """Display assistant message with rich formatting"""
        # Try to render as markdown if it contains markdown-like content
        if any(marker in content for marker in ['```', '**', '*', '#', '|']):
            try:
                markdown = Markdown(content)
                console.print(Panel(
                    markdown,
                    title="🤖 Assistant",
                    border_style="blue"
                ))
                return
            except Exception:
                pass  # Fall back to plain text
        
        # Plain text display
        console.print(Panel(
            content,
            title="🤖 Assistant",
            border_style="blue"
        ))
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        tool_descriptions = []
        if self.mcp_client.tools:
            for tool_name, tool in self.mcp_client.tools.items():
                server_name = tool_name.split(":")[0]
                tool_descriptions.append(f"- {tool.name} (from {server_name}): {tool.description}")
        
        tools_text = "\n".join(tool_descriptions) if tool_descriptions else "No tools available"
        
        if self.is_ollama_model and self.mcp_client.tools:
            # For Ollama models, be direct about the limitation
            return f"""You are a helpful AI assistant running as a local Ollama model.

Important: You cannot automatically call MCP tools because Ollama models don't support function calling.

Available MCP tools (for manual use):
{tools_text}

When users ask about tasks that would require these tools:
1. Clearly explain that you cannot automatically call the tools
2. Describe which tool would be helpful for their request
3. Suggest they use the command-line interface to call tools manually
4. Provide guidance on MCP tool usage

Be honest about your limitations while still being helpful and informative."""
        else:
            # For cloud models with function calling support
            return f"""You are a helpful AI assistant with access to MCP (Model Context Protocol) tools. 
You can help users by calling these tools when appropriate.

Available MCP tools:
{tools_text}

When using tools:
1. Choose the most appropriate tool for the user's request
2. Provide clear explanations of what you're doing
3. Interpret and summarize tool results for the user
4. If a tool fails, explain what went wrong and suggest alternatives

Be conversational, helpful, and make good use of the available tools to assist the user."""
    
    async def start_interactive(self):
        """Start interactive chat session"""
        # Validate model availability first
        if not await self.validate_model():
            return
        
        self._show_welcome_banner()
        self.running = True
        
        try:
            while self.running:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                
                if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                    console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif user_input.lower() == '/help':
                    self._show_help()
                elif user_input.lower() == '/tools':
                    self.mcp_client.show_tools()
                elif user_input.lower() == '/status':
                    self.mcp_client.show_status()
                elif user_input.lower() == '/model':
                    console.print(f"[cyan]Current model: [bold]{self.model}[/bold][/cyan]")
                elif user_input.lower() == '/models':
                    await self.mcp_client.show_ollama_models()
                elif user_input.lower() == '/clear':
                    self.conversation_history.clear()
                    console.print("[green]✅ Conversation history cleared[/green]")
                elif user_input.strip():
                    await self.process_message(user_input)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Chat session error: {e}[/red]")
    
    def _show_help(self):
        """Show help information"""
        help_text = """[bold cyan]MCP Shell Chat Commands[/bold cyan]

[yellow]Chat Commands:[/yellow]
  /help     - Show this help message
  /tools    - List available MCP tools
  /status   - Show MCP server connection status
  /model    - Show current LLM model
  /models   - List available models
  /clear    - Clear conversation history
  /exit     - Exit chat mode

[yellow]Usage Tips:[/yellow]
• Ask questions naturally - I'll use MCP tools when helpful
• Request specific tasks like "list files" or "search for X"
• I can explain tool results and help interpret data
• Tools are called automatically based on your requests

[yellow]Example Requests:[/yellow]
• "List the files in my home directory"
• "Search for Python tutorials online"
• "What's the current status of my git repository?"
• "Help me write a function to calculate fibonacci numbers"
"""
        console.print(Panel(help_text, border_style="blue"))
    
    async def close(self):
        """Close the chat session"""
        self.running = False 