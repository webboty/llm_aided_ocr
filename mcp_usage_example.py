#!/usr/bin/env python3
"""
Example usage of LLM-Aided OCR MCP Server
This demonstrates how to use the MCP server with Claude Desktop or other MCP clients
"""

import asyncio
import json
from pathlib import Path

# Example Claude Desktop configuration
CLAUDE_DESKTOP_CONFIG = {
    "mcpServers": {
        "llm-aided-ocr": {
            "command": "python",
            "args": ["mcp_server.py"],
            "cwd": str(Path(__file__).parent.absolute()),
            "env": {"RESULTS_DIR": "results"},
        }
    }
}


def print_claude_config():
    """Print Claude Desktop configuration"""
    print("🤖 Claude Desktop Configuration")
    print("=" * 40)
    print("Add this to your Claude Desktop configuration file:")
    print()

    config_path = {
        "macOS": "~/Library/Application Support/Claude/claude_desktop_config.json",
        "Windows": "%APPDATA%\\Claude\\claude_desktop_config.json",
        "Linux": "~/.config/claude/claude_desktop_config.json",
    }

    for platform, path in config_path.items():
        print(f"{platform}: {path}")
    print()

    print(json.dumps(CLAUDE_DESKTOP_CONFIG, indent=2))
    print()
    print("After adding this configuration, restart Claude Desktop.")


def print_usage_examples():
    """Print usage examples"""
    print("💡 Usage Examples with Claude Desktop")
    print("=" * 45)
    print()

    examples = [
        {
            "prompt": "Process this PDF file: /path/to/document.pdf",
            "description": "Basic PDF processing with default settings",
        },
        {
            "prompt": "Process this scanned contract using OpenAI: /path/to/contract.pdf",
            "description": "Specify LLM provider",
        },
        {
            "prompt": "Process this presentation using LM Studio with Qwen model: /path/to/slides.pdf",
            "description": "Specify provider and model",
        },
        {
            "prompt": "Check the status of my OCR jobs",
            "description": "List all processing jobs",
        },
        {
            "prompt": "Show me the corrected output from job 12345678-1234-1234-1234-123456789abc",
            "description": "Access specific job results",
        },
        {
            "prompt": "Clean up completed OCR jobs older than 1 day",
            "description": "Job management",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['prompt']}")
        print(f"   → {example['description']}")
        print()


def print_mcp_tools():
    """Print available MCP tools"""
    print("🛠️ Available MCP Tools")
    print("=" * 30)
    print()

    tools = [
        {
            "name": "process_pdf",
            "description": "Process a PDF file with OCR and LLM correction",
            "parameters": [
                "pdf_path (required): Path to PDF file",
                "provider (optional): LLM provider (openai, claude, lm-studio)",
                "model (optional): Model name for lm-studio",
                "output_path (optional): Custom output directory",
            ],
        },
        {
            "name": "get_job_status",
            "description": "Get the status of a processing job",
            "parameters": ["job_id (required): Job identifier"],
        },
        {
            "name": "list_jobs",
            "description": "List all processing jobs",
            "parameters": [],
        },
        {
            "name": "delete_job",
            "description": "Delete a job and its associated files",
            "parameters": ["job_id (required): Job identifier"],
        },
    ]

    for tool in tools:
        print(f"🔧 {tool['name']}")
        print(f"   {tool['description']}")
        if tool["parameters"]:
            print("   Parameters:")
            for param in tool["parameters"]:
                print(f"   • {param}")
        print()


def print_mcp_resources():
    """Print available MCP resources"""
    print("📁 MCP Resources")
    print("=" * 20)
    print()

    print("Processed files are available as MCP resources:")
    print()
    print("📄 Raw OCR output:")
    print("   ocr://job/{job_id}/raw_ocr")
    print()
    print("📝 LLM-corrected output:")
    print("   ocr://job/{job_id}/corrected")
    print()
    print("Example:")
    print("   ocr://job/12345678-1234-1234-1234-123456789abc/corrected")
    print()


def main():
    """Main function"""
    print("🚀 LLM-Aided OCR MCP Server Usage Guide")
    print("=" * 50)
    print()

    print_claude_config()
    print_usage_examples()
    print_mcp_tools()
    print_mcp_resources()

    print("📖 For complete documentation, see MCP_README.md")
    print()
    print("🧪 To test the MCP server, run:")
    print("   python test_mcp.py")
    print()
    print("🔧 To configure LLM providers, run:")
    print("   python config_helper.py")


if __name__ == "__main__":
    main()
