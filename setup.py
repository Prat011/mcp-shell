#!/usr/bin/env python3
"""
Setup script for MCP Shell
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    requirements = []
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
else:
    requirements = [
        "click>=8.0.0",
        "rich>=13.0.0", 
        "aiohttp>=3.8.0",
        "litellm>=1.0.0"
    ]

setup(
    name="mcp-terminal",
    version="1.0.0",
    author="MCP Shell Team",
    author_email="dev@mcpterminal.com",
    description="A powerful shell-based Model Context Protocol client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcpterminal/mcp-terminal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-terminal=mcp_terminal.cli:main",
        ],
    },
    keywords="mcp model-context-protocol terminal cli chat llm ai tools",
    project_urls={
        "Bug Reports": "https://github.com/mcpterminal/mcp-terminal/issues",
        "Source": "https://github.com/mcpterminal/mcp-terminal",
        "Documentation": "https://github.com/mcpterminal/mcp-terminal#readme",
    },
) 