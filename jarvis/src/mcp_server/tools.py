"""
MCP Tools - Python functions exposed via MCP server.

These functions can be called by the LLM agent.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def print_action(message: str) -> Dict[str, Any]:
    """
    Print a message to the console.
    
    This is a simple action function that the LLM can call.
    
    Args:
        message: The message to print
        
    Returns:
        Dictionary with success status and result
    """
    print(f"\n[ACTION] {message}")
    logger.info(f"Action executed: {message}")
    
    return {
        "success": True,
        "result": f"Printed message: {message}",
        "function": "print_action"
    }


# Registry of available tools
AVAILABLE_TOOLS = {
    "print_action": {
        "function": print_action,
        "description": "Prints a message to the console. Use this when you want to output information or confirm actions.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to print"
                }
            },
            "required": ["message"]
        }
    }
}


def get_tool(name: str):
    """Get a tool function by name."""
    if name in AVAILABLE_TOOLS:
        return AVAILABLE_TOOLS[name]["function"]
    raise ValueError(f"Tool '{name}' not found")


def list_tools() -> Dict[str, Dict]:
    """List all available tools."""
    return AVAILABLE_TOOLS
