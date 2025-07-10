"""
Configuration Management for MCP Shell

Handles loading and saving of MCP server configurations
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from .core import MCPServerConfig, TransportType


class ConfigManager:
    """Manages MCP Shell configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._ensure_config_dir()
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path"""
        # Use XDG_CONFIG_HOME if available, otherwise use ~/.config
        config_home = os.environ.get('XDG_CONFIG_HOME')
        if config_home:
            config_dir = Path(config_home)
        else:
            config_dir = Path.home() / '.config'
        
        return config_dir / 'mcp-terminal' / 'config.json'
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error: Failed to save config to {self.config_path}: {e}")
    
    def load_servers(self) -> List[MCPServerConfig]:
        """Load server configurations"""
        config = self.load_config()
        servers = []
        
        for server_data in config.get('servers', []):
            try:
                # Convert transport string to enum
                transport_str = server_data.get('transport', 'stdio')
                transport = TransportType(transport_str)
                
                server_config = MCPServerConfig(
                    name=server_data['name'],
                    transport=transport,
                    command=server_data.get('command'),
                    args=server_data.get('args'),
                    env=server_data.get('env'),
                    cwd=server_data.get('cwd'),
                    url=server_data.get('url'),
                    headers=server_data.get('headers'),
                    description=server_data.get('description'),
                    timeout=server_data.get('timeout', 30)
                )
                servers.append(server_config)
            except (KeyError, ValueError) as e:
                print(f"Warning: Invalid server config: {e}")
                continue
        
        return servers
    
    def save_servers(self, servers: List[MCPServerConfig]):
        """Save server configurations"""
        config = self.load_config()
        
        # Convert server configs to dictionaries
        server_data = []
        for server in servers:
            data = {
                'name': server.name,
                'transport': server.transport.value,
                'description': server.description,
                'timeout': server.timeout
            }
            
            # Add transport-specific fields
            if server.transport == TransportType.STDIO:
                data.update({
                    'command': server.command,
                    'args': server.args,
                    'env': server.env,
                    'cwd': server.cwd
                })
            elif server.transport in (TransportType.HTTP, TransportType.SSE):
                data.update({
                    'url': server.url,
                    'headers': server.headers
                })
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            server_data.append(data)
        
        config['servers'] = server_data
        self.save_config(config)
    
    def add_server(self, server: MCPServerConfig):
        """Add a new server configuration"""
        servers = self.load_servers()
        
        # Remove existing server with same name if exists
        servers = [s for s in servers if s.name != server.name]
        
        # Add new server
        servers.append(server)
        
        # Save updated list
        self.save_servers(servers)
    
    def remove_server(self, name: str) -> bool:
        """Remove a server configuration
        
        Returns:
            bool: True if server was found and removed, False if not found
        """
        servers = self.load_servers()
        original_count = len(servers)
        servers = [s for s in servers if s.name != name]
        
        if len(servers) == original_count:
            return False  # Server not found
        
        self.save_servers(servers)
        return True  # Server was removed
    
    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """Get a specific server configuration"""
        servers = self.load_servers()
        for server in servers:
            if server.name == name:
                return server
        return None
    
    def update_setting(self, key: str, value: Any):
        """Update a configuration setting"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        config = self.load_config()
        return config.get(key, default)
    
    # Ollama-specific configuration methods
    def get_ollama_base_url(self) -> str:
        """Get Ollama base URL"""
        return self.get_setting('ollama.base_url', 'http://localhost:11434')
    
    def set_ollama_base_url(self, url: str):
        """Set Ollama base URL"""
        self.update_setting('ollama.base_url', url)
    
    def get_default_model(self) -> str:
        """Get default model preference"""
        return self.get_setting('default_model', 'gpt-4o-mini')
    
    def set_default_model(self, model: str):
        """Set default model preference"""
        self.update_setting('default_model', model)
    
    def get_ollama_auto_pull(self) -> bool:
        """Get whether to auto-pull missing Ollama models"""
        return self.get_setting('ollama.auto_pull', True)
    
    def set_ollama_auto_pull(self, auto_pull: bool):
        """Set whether to auto-pull missing Ollama models"""
        self.update_setting('ollama.auto_pull', auto_pull)
    
    def get_preferred_ollama_models(self) -> List[str]:
        """Get list of preferred Ollama models to show first"""
        return self.get_setting('ollama.preferred_models', [
            'llama3.2',
            'llama3.1',
            'codellama',
            'mistral',
            'gemma2'
        ])
    
    def add_preferred_ollama_model(self, model: str):
        """Add a model to preferred Ollama models"""
        models = self.get_preferred_ollama_models()
        if model not in models:
            models.insert(0, model)  # Add to top
            self.update_setting('ollama.preferred_models', models)
    
    def create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = {
            "default_model": "gpt-4o-mini",
            "ollama": {
                "base_url": "http://localhost:11434",
                "auto_pull": True,
                "preferred_models": [
                    "llama3.2",
                    "llama3.1", 
                    "codellama",
                    "mistral",
                    "gemma2"
                ]
            },
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
        
        if not self.config_path.exists():
            self.save_config(sample_config)
            return True
        return False 