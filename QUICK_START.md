# MCP Shell - Launch Ready! 🚀

## Get Started in 3 Minutes

### 1. Install
```bash
# Option A: Install from this directory
pip install -e .

# Option B: Install requirements directly
pip install -r requirements.txt
```

### 2. Set API Key (Choose one)
```bash
# OpenAI (recommended - supports latest models)
export OPENAI_API_KEY="your-openai-api-key-here"

# Or Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Or Google
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 3. Run!
```bash
# Start interactive chat (will show model selection menu)
mcp-shell chat

# Or specify a model directly
mcp-shell chat --model gpt-4o

# Ask a single question
mcp-shell ask "Write a Python function to reverse a string"

# Run demo
python demo.py
```

## Usage Examples

### Basic Chat with Model Selection
```bash
$ mcp-shell chat

 ███╗   ███╗ ██████╗██████╗     ███████╗██╗  ██╗███████╗██╗     ██╗     
 ████╗ ████║██╔════╝██╔══██╗    ██╔════╝██║  ██║██╔════╝██║     ██║     
 ██╔████╔██║██║     ██████╔╝    ███████╗███████║█████╗  ██║     ██║     
 ██║╚██╔╝██║██║     ██╔═══╝     ╚════██║██╔══██║██╔══╝  ██║     ██║     
 ██║ ╚═╝ ██║╚██████╗██║         ███████║██║  ██║███████╗███████╗███████╗
 ╚═╝     ╚═╝ ╚═════╝╚═╝         ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝

🚀 Select a model:

⭐ Popular Models:
   1. OpenAI GPT-4o (Latest GPT)
   2. OpenAI GPT-4o Mini (Fast & Cheap)
   3. Anthropic Claude Sonnet 4 (Latest Claude)
   4. Anthropic Claude 3.5 Sonnet (Reliable)
   5. Google Gemini 2.5 Flash (Latest Gemini)
   6. DeepSeek R1 (Strong Reasoning)
   7. Meta Llama 4 Scout (Latest Llama)

   8. 🔍 Browse all models by provider
   9. ⚡ Use default (gpt-4o-mini)

🎯 Enter your choice: 2

🚀 Starting MCP Shell...
Current Model: gpt-4o-mini
Connected Servers: 0
Available Tools: 0

You: Hello! Can you help me write a quicksort algorithm?

🤖 Assistant: I'd be happy to help you implement quicksort!
[... AI response with code ...]
```

### With MCP Servers
```bash
$ mcp-shell chat --servers filesystem,git --model claude-sonnet-4-20250514

🔌 Connecting to MCP servers...
✅ Connected to filesystem
✅ Connected to git

🚀 Starting MCP Shell...
Current Model: claude-sonnet-4-20250514
Connected Servers: 2
Available Tools: 5

You: Can you list the files in the current directory and check the git status?

🤖 Assistant: I'll help you check the files and git status!

🔧 Executing tool: filesystem:list_files
✅ Tool Result: [...file list...]

🔧 Executing tool: git:status  
✅ Tool Result: [...git status...]

Based on the results, here's what I found:
[... AI analysis of the results ...]
```

### Available Commands
```bash
# List all available models
mcp-shell models

# List available MCP servers
mcp-shell servers --list

# Connect to remote MCP server via URL
mcp-shell chat --servers https://api.example.com/mcp

# Quick single question
mcp-shell ask "What's the latest in AI?" --model deepseek-r1
```

### MCP Server Optionsls (Optional)
```bash
# First install MCP servers (optional)
npm install -g @modelcontextprotocol/server-filesystem

# Then connect tools
mcp-shell chat --servers filesystem

You: Read my README.md file and summarize it

🔧 Executing tool: read_file
└─ Args: {"path": "README.md"}
└─ Result: File contents loaded

🤖 Assistant: Based on your README.md file, here's a summary:
[... AI analyzes your actual file ...]
```

### Switch Models on the Fly
```bash
You: /model claude-3-haiku-20240307
✅ Switched to model: claude-3-haiku-20240307

You: /model gpt-4
✅ Switched to model: gpt-4
```

## Available Commands
- `/help` - Show help
- `/model <name>` - Switch LLM model  
- `/status` - Show current status
- `/clear` - Clear conversation
- `/exit` - Exit

## Supported Models
Any model from [LiteLLM](https://litellm.vercel.app/docs/providers):
- `gpt-4`, `gpt-3.5-turbo` (OpenAI)
- `claude-3-sonnet-20240229` (Anthropic) 
- `gemini-pro` (Google)
- `ollama/llama3.2` (Local via Ollama)
- `groq/llama-3.1-70b-versatile` (Groq)

## Troubleshooting

### "No API key provided"
```bash
export OPENAI_API_KEY="sk-..."
# Or use any provider key:
export ANTHROPIC_API_KEY="..."
export GOOGLE_API_KEY="..."
```

### "MCP SDK not installed" 
This is just a warning - basic functionality works without it. To use MCP tools:
```bash
pip install mcp  # Official MCP Python SDK
```

### "Module not found"
Make sure you're in the project directory and run:
```bash
pip install -e .
```

## Ready to Launch? 

**You can ship this today!** The core functionality works without any MCP servers. Users can:

1. ✅ Chat with any LLM model via LiteLLM
2. ✅ Switch models during conversation  
3. ✅ Rich terminal interface with markdown
4. ✅ Zero configuration needed
5. ✅ Works with all major LLM providers

MCP server integration is optional and can be added later.

---

**🎉 Your terminal AI assistant is ready to go!** 