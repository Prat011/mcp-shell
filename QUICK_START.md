# MCP Shell - Launch Ready! 🚀

## Get Started in 3 Minutes

### 1. Install
```bash
# Option A: Install from this directory
pip install -e .

# Option B: Install requirements directly
pip install -r requirements.txt
```

### 2. Choose Your LLM Provider

#### Option A: Cloud Models (API Key Required)
```bash
# OpenAI (recommended - supports latest models)
export OPENAI_API_KEY="your-openai-api-key-here"

# Or Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Or Google
export GOOGLE_API_KEY="your-google-api-key-here"

# Or Groq
export GROQ_API_KEY="your-groq-api-key-here"
```

#### Option B: Local Models with Ollama (No API Key Needed! 🦙)
```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama service
ollama serve

# 3. Pull a model (choose one)
ollama pull llama3.3:70b       # Recommended: Latest Llama model
ollama pull llama3.2           # Fast and capable
ollama pull codellama          # Great for coding
ollama pull mistral            # Efficient alternative
ollama pull gemma2             # Google's model
ollama pull deepseek-r1        # Strong reasoning capabilities

# 4. Ready to use! No API key needed
```

### 3. Run!
```bash
# Start interactive chat (will show model selection menu)
mcp-shell chat

# Or specify a model directly
mcp-shell chat --model gpt-4.1                    # Cloud model
mcp-shell chat --model ollama/llama3.3:70b       # Local Ollama model

# Ask a single question
mcp-shell ask "Write a Python function to reverse a string"

# Run demo
python demo.py
```

## Usage Examples

### Basic Chat with Model Selection
```bash
$ mcp-shell chat

+=========================================+
|  ███╗   ███╗ ██████╗██████╗             |
|  ████╗ ████║██╔════╝██╔══██╗            |
|  ██╔████╔██║██║     ██████╔╝            |
|  ██║╚██╔╝██║██║     ██╔═══╝             |
|  ██║ ╚═╝ ██║╚██████╗██║                 |
|  ╚═╝     ╚═╝ ╚═════╝╚═╝                 |
|                                         |
| ███████╗██╗  ██╗███████╗██╗     ██╗     |
| ██╔════╝██║  ██║██╔════╝██║     ██║     |
| ███████╗███████║█████╗  ██║     ██║     |
| ╚════██║██╔══██║██╔══╝  ██║     ██║     |
| ███████║██║  ██║███████╗███████╗███████╗|
| ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝|
|                                         |
+=========================================+

🚀 Select a model:

⭐ Popular Models:
   1. OpenAI GPT-4.1 (Latest GPT)
   2. OpenAI GPT-4.5 (Enhanced with "Vibe Check")
   3. OpenAI o3-mini (Latest reasoning model)
   4. Anthropic Claude 4 Sonnet (Latest Claude)
   5. Anthropic Claude 4 Opus (Most capable Claude)
   6. Google Gemini 2.5 Flash (Latest Gemini)
   7. Google Gemini 2.5 Pro (Enhanced reasoning)
   8. DeepSeek R1 (Strong reasoning & cost-effective)

🦙 Local Ollama Models:
   9. Ollama: llama3.3:70b (Latest Llama)
   10. Ollama: deepseek-r1 (Strong reasoning)
   11. Ollama: llama3.2 (Fast & capable)
   12. Ollama: codellama (Coding specialist)
   13. Ollama: mistral (Efficient)

   14. 🔍 Browse all models by provider
   15. ⚡ Use default (gpt-4o-mini)

🎯 Enter your choice: 9

🚀 Starting MCP Shell...
Current Model: ollama/llama3.3:70b (Local via Ollama)
Connected Servers: 0
Available Tools: 0

You: Hello! Can you help me write a quicksort algorithm?

🤖 Assistant: I'd be happy to help you implement quicksort!
[... AI response with code ...]
```

### With MCP Servers
```bash
$ mcp-shell chat --servers filesystem,git --model claude-4-sonnet-20250514

🔌 Connecting to MCP servers...
✅ Connected to filesystem
✅ Connected to git

🚀 Starting MCP Shell...
Current Model: claude-4-sonnet-20250514
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

# Use local Ollama models (no API key needed!)
mcp-shell chat --model ollama/llama3.3:70b
mcp-shell ask "Explain quantum computing" --model ollama/deepseek-r1
```

### MCP Server Options (Optional)
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
You: /model claude-4-sonnet-20250514
✅ Switched to model: claude-4-sonnet-20250514

You: /model o3-mini
✅ Switched to model: o3-mini
```

## Available Commands
- `/help` - Show help
- `/model <name>` - Switch LLM model  
- `/status` - Show current status
- `/clear` - Clear conversation
- `/exit` - Exit

## Supported Models

### 🦙 Local Models (Ollama) - Privacy First!
- `ollama/llama3.3:70b` - Latest Llama model with enhanced capabilities
- `ollama/deepseek-r1` - Excellent reasoning capabilities, cost-effective
- `ollama/llama3.2` - Fast and capable, perfect for most tasks
- `ollama/codellama` - Specialized for coding tasks
- `ollama/mistral` - Efficient and fast European model
- `ollama/gemma2` - Google's open model
- **Benefits**: No API costs, full privacy, works offline, fast inference

### ☁️ Cloud Models
Latest models from [LiteLLM](https://litellm.vercel.app/docs/providers):

#### OpenAI
- `gpt-4.1` - Latest GPT-4 model
- `gpt-4.5` - Enhanced with "Vibe Check" capabilities
- `o3-mini` - Latest reasoning model (replaces o1-mini)
- `o1` - Original reasoning model

#### Anthropic
- `claude-4-sonnet-20250514` - Latest Claude 4 Sonnet
- `claude-4-opus-20250514` - Most capable Claude model
- `claude-3-5-sonnet-20241022` - Previous generation

#### Google
- `gemini-2.5-flash` - Latest Gemini model
- `gemini-2-pro` - Enhanced reasoning capabilities
- `gemini-1.5-flash` - Previous generation

#### Others
- `deepseek-r1` - Strong reasoning, cost-effective
- `groq/llama-3.3-70b-versatile` - Fast inference via Groq

## 🦙 Using Ollama (Local Models)

### Quick Start with Ollama
```bash
# 1. Install Ollama (one-time setup)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama service
ollama serve

# 3. Pull recommended model  
ollama pull llama3.3:70b

# 4. Use immediately in MCP Shell
mcp-shell chat --model ollama/llama3.3:70b
```

### Ollama Features in MCP Shell
- 🔍 **Auto-discovery**: Automatically detects installed Ollama models
- 📥 **Auto-pull**: Offers to download missing models when needed
- 🚀 **Interactive selection**: Browse and select from available local models
- ⚡ **Fast inference**: Local processing with no network latency
- 🔒 **Complete privacy**: All processing happens on your machine
- 💰 **Zero costs**: No API keys or usage fees

### Popular Ollama Models for Different Tasks

#### General Purpose (Latest)
```bash
ollama pull llama3.3:70b      # Latest Llama - best overall performance
ollama pull deepseek-r1       # Excellent reasoning capabilities
ollama pull llama3.2          # Fast, good for most tasks
ollama pull llama3.1:8b       # Balanced performance
```

#### Coding Specialized  
```bash
ollama pull codellama         # Meta's code-specialized model
ollama pull deepseek-coder    # Excellent for programming tasks
ollama pull starcoder2        # Code generation and completion
```

#### Efficient Models
```bash
ollama pull gemma2:2b         # Google's efficient 2B model
ollama pull mistral:7b        # Mistral's balanced 7B model
ollama pull phi3.5           # Microsoft's efficient model
```

#### Reasoning Models
```bash
ollama pull deepseek-r1       # Strong reasoning through RL training
ollama pull llama3.3:70b      # Latest with enhanced reasoning
```

### Ollama Commands
```bash
# List available models
ollama list

# Pull a specific model
ollama pull llama3.3:70b

# Remove a model to save space
ollama rm old-model

# Show model information
ollama show llama3.3:70b

# Check Ollama status
ollama ps
```

## Troubleshooting

### Ollama Issues

#### "Ollama is not running"
```bash
# Start Ollama service
ollama serve

# Or if on macOS with Homebrew
brew services start ollama
```

#### "Model not found"
```bash
# List available models
ollama list

# Pull the model you want
ollama pull llama3.3:70b

# Check available models on Ollama Hub
curl https://ollama.com/api/tags
```

#### "Out of memory" or slow performance
```bash
# Use smaller models for limited hardware
ollama pull gemma2:2b         # 2B parameters
ollama pull llama3.2:1b       # 1B parameters

# Or check memory usage
ollama ps
```

### Cloud Model Issues

#### "No API key provided"
```bash
export OPENAI_API_KEY="sk-..."
# Or use any provider key:
export ANTHROPIC_API_KEY="..."
export GOOGLE_API_KEY="..."
```

### General Issues

#### "MCP SDK not installed" 
This is just a warning - basic functionality works without it. To use MCP tools:
```bash
pip install mcp  # Official MCP Python SDK
```

#### "Module not found"
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

**🎉 Your terminal AI assistant is ready to go!**s