```
███╗   ███╗ ██████╗██████╗     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     
████╗ ████║██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     
██╔████╔██║██║     ██████╔╝       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     
██║╚██╔╝██║██║     ██╔═══╝        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     
██║ ╚═╝ ██║╚██████╗██║            ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
╚═╝     ╚═╝ ╚═════╝╚═╝            ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
```

# 🚀 MCP Terminal

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MCP Terminal** is a powerful, modern terminal-based client for the **Model Context Protocol (MCP)**. It provides both direct tool execution capabilities and interactive chat mode with LLM integration, making it easy to interact with MCP servers from the command line.

```
 🤖 MCP Terminal - Your AI-Powered Command Line Companion

 Features:
 • Direct MCP tool execution from command line
 • Interactive chat mode with LLM integration  
 • Support for stdio and HTTP MCP servers
 • Rich terminal UI with beautiful formatting
 • Multiple LLM provider support (OpenAI, Anthropic, Google, etc.)
 • Persistent server configuration
 • Tool discovery and help system
```

## ✨ Features

### 🔧 **Direct Tool Execution**
Execute MCP tools directly from the command line with automatic parameter collection:
```bash
mcp-terminal tool list_files
mcp-terminal tool search_web --query "Python tutorials"
```

### 💬 **Interactive Chat Mode**
Chat naturally with an AI assistant that automatically uses MCP tools:
```bash
mcp-terminal chat
> "List the files in my project directory"
> "Search for information about async Python"
```

### 🔌 **Multiple Transport Support**
- **stdio**: Connect to local MCP servers via stdin/stdout
- **HTTP**: Connect to remote MCP servers via HTTP/REST APIs

### 🎨 **Rich Terminal UI**
- Beautiful table displays for tools and servers
- Syntax highlighted code blocks
- Markdown rendering in chat mode
- Progress indicators and status updates

### 🤖 **LLM Integration**
Support for multiple LLM providers through LiteLLM:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Groq, Ollama, and more

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/mcpterminal/mcp-terminal.git
cd mcp-terminal
pip install -e .

# Or install from PyPI (when published)
pip install mcp-terminal
```

### Basic Usage

1. **Add an MCP server:**
```bash
mcp-terminal server add
```

2. **List available tools:**
```bash
mcp-terminal tools
```

3. **Execute a tool:**
```bash
mcp-terminal tool <tool_name>
```

4. **Start chat mode:**
```bash
export OPENAI_API_KEY="your-api-key"
mcp-terminal chat
```

## 📖 Usage Guide

### Server Management

**Add a stdio server:**
```bash
mcp-terminal server add
# Follow the interactive prompts:
# Server name: filesystem  
# Transport type: stdio
# Command: npx
# Arguments: @modelcontextprotocol/server-filesystem /tmp
```

**Add an HTTP server:**
```bash
mcp-terminal server add
# Follow the interactive prompts:
# Server name: remote-mcp
# Transport type: http  
# Server URL: http://localhost:8000/mcp
```

**List configured servers:**
```bash
mcp-terminal server list
```

**Show server status:**
```bash
mcp-terminal server status
```

### Tool Execution

**List all available tools:**
```bash
mcp-terminal tools
```

**Get help for a specific tool:**
```bash
mcp-terminal tool-help read_file
```

**Execute a tool interactively:**
```bash
mcp-terminal tool read_file
# You'll be prompted for required parameters
```

### Chat Mode

**Start interactive chat:**
```bash
export OPENAI_API_KEY="your-openai-key"
mcp-terminal chat
```

**Use a specific model:**
```bash
mcp-terminal chat --model claude-3-5-sonnet-20241022
```

### Available Models

**OpenAI Models:**
- `gpt-4.1` - Latest GPT-4.1 (default)
- `gpt-4.1-mini` - Efficient GPT-4.1 variant
- `gpt-4.1-nano` - Lightweight GPT-4.1 variant
- `o3` - Latest reasoning model (limited access)
- `gpt-4o` - GPT-4 Omni multimodal
- `gpt-4o-mini` - Efficient GPT-4 Omni

**Anthropic Claude Models:**
- `claude-3-5-sonnet-20241022` - Latest Claude 3.5 Sonnet
- `claude-3-5-haiku-20241022` - Fast Claude 3.5 model
- `claude-3-7-sonnet-20250215` - Advanced Claude 3.7 Sonnet
- `claude-4-opus-20250515` - Claude 4 Opus (most capable)
- `claude-4-sonnet-20250515` - Claude 4 Sonnet

**Google Gemini Models:**
- `gemini-2.5-pro` - Latest Gemini 2.5 Pro (experimental)
- `gemini-2.5-flash` - Fast Gemini 2.5 model
- `gemini-1.5-pro` - Production Gemini 1.5 Pro
- `gemini-1.5-flash` - Efficient Gemini 1.5 model

**Ask a single question:**
```bash
mcp-terminal ask "What files are in my current directory?"
```

**Chat commands:**
- `/help` - Show help
- `/tools` - List available tools
- `/status` - Show server status  
- `/clear` - Clear conversation
- `/exit` - Exit chat

## 🔧 Configuration

MCP Terminal stores configuration in `~/.config/mcp-terminal/config.json`:

```json
{
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "command": "npx", 
      "args": ["@modelcontextprotocol/server-filesystem", "/tmp"],
      "description": "Local filesystem server"
    },
    {
      "name": "remote-mcp",
      "transport": "http",
      "url": "http://localhost:8000/mcp",
      "description": "Remote MCP server"
    }
  ]
}
```

## 🌐 MCP Server Examples

### Popular MCP Servers

**Filesystem Server (Node.js):**
```bash
npm install -g @modelcontextprotocol/server-filesystem
# Use with: npx @modelcontextprotocol/server-filesystem /path/to/directory
```

**Git Server (Python):**
```bash
pip install mcp-server-git
# Use with: python -m mcp_server_git
```

**Terminal Server (for command execution):**
```bash
npm install -g @rinardnick/mcp-terminal
# Use with: npx @rinardnick/mcp-terminal
```

**Web Search Server:**
```bash
npm install -g @modelcontextprotocol/server-web-search
# Use with: npx @modelcontextprotocol/server-web-search
```

### Creating Custom Servers

You can create custom MCP servers in any language that supports JSON-RPC 2.0. See the [MCP specification](https://spec.modelcontextprotocol.io/) for details.

## 🔑 API Keys

Set your LLM API key via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic  
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="AI..."

# Groq
export GROQ_API_KEY="gsk_..."
```

## 💡 Examples

### File Management
```bash
# Add filesystem server
mcp-terminal server add
# Configure as stdio server with command: npx @modelcontextprotocol/server-filesystem /

# Chat mode
mcp-terminal chat
> "List all Python files in my project"
> "Read the contents of main.py"
> "Create a new file called test.py with a hello world function"
```

### Web Research
```bash  
# Add web search server
mcp-terminal server add
# Configure as stdio server with command: npx @modelcontextprotocol/server-web-search

# Chat mode
mcp-terminal chat
> "Search for the latest Python asyncio best practices"
> "Find tutorials about Model Context Protocol"
```

### Git Operations
```bash
# Add git server
mcp-terminal server add
# Configure as stdio server with command: python -m mcp_server_git

# Direct tool usage
mcp-terminal tool git_status
mcp-terminal tool git_log --max_entries 5

# Chat mode
mcp-terminal chat
> "What's the current status of my git repository?"
> "Show me the last 5 commits"
> "Create a new branch called feature/mcp-integration"
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/mcpterminal/mcp-terminal.git
cd mcp-terminal

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black mcp_terminal/

# Type checking  
mypy mcp_terminal/
```

### Project Structure

```
mcp_terminal/
├── __init__.py          # Package initialization
├── core.py              # Core MCP client implementation
├── cli.py               # Command-line interface
├── chat.py              # Interactive chat session
└── config.py            # Configuration management
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the excellent protocol specification
- [LiteLLM](https://github.com/BerriAI/litellm) for multi-provider LLM support
- [Rich](https://github.com/Textualize/rich) for beautiful terminal formatting
- [Click](https://github.com/pallets/click) for the CLI framework

## 📞 Support

- 🐛 [Report Issues](https://github.com/mcpterminal/mcp-terminal/issues)
- 💬 [Discussions](https://github.com/mcpterminal/mcp-terminal/discussions)
- 📖 [Documentation](https://github.com/mcpterminal/mcp-terminal#readme)

---

**Made with ❤️ for the MCP community** 