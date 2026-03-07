"""
MCP (Model Context Protocol) Server implementation.

Exposes Python functions as tools that the LLM agent can call.
"""

import logging
from typing import Dict, Any, List, Optional
from .tools import AVAILABLE_TOOLS, get_tool, list_tools

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server that exposes tools for the LLM agent to call."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools = list_tools()
        logger.info(f"MCP Server initialized with {len(self.tools)} tools")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools in MCP format.
        
        Returns:
            List of tool definitions
        """
        tool_list = []
        for tool_name, tool_info in self.tools.items():
            tool_list.append({
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": tool_info["parameters"]
            })
        return tool_list
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool by name with the given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
            
        Returns:
            Result dictionary with success status and result
        """
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(self.tools.keys())
                }
            
            tool_func = get_tool(tool_name)
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            # Call the tool function with the arguments
            result = tool_func(**arguments)
            
            logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except TypeError as e:
            error_msg = f"Invalid arguments for tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def execute_function_call(self, function_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call from the LLM agent.
        
        Expected format: {
            'function': 'tool_name',
            'args': ['arg1', 'arg2', ...] or {'arg1': 'value1', ...}
        }
        
        Args:
            function_call: Dictionary with 'function' and 'args' keys
            
        Returns:
            Result dictionary
        """
        tool_name = function_call.get('function')
        args = function_call.get('args', [])
        
        if not tool_name:
            return {
                "success": False,
                "error": "Function name not provided"
            }
        
        # Convert list of args to dict if needed
        # For print_action, we expect a single message argument
        if isinstance(args, list):
            # If it's a list, try to map to function parameters
            # For print_action, first arg is message
            if tool_name == "print_action" and len(args) > 0:
                arguments = {"message": args[0]}
            else:
                # Generic mapping - use positional args
                tool_info = self.tools.get(tool_name, {})
                params = tool_info.get("parameters", {}).get("properties", {})
                param_names = list(params.keys())
                arguments = {}
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        arguments[param_names[i]] = arg
        else:
            arguments = args
        
        return self.call_tool(tool_name, arguments)
    
    def get_tool_descriptions_for_prompt(self) -> str:
        """
        Get tool descriptions formatted for LLM prompts.
        
        Returns:
            Formatted string describing available tools
        """
        descriptions = []
        for tool_name, tool_info in self.tools.items():
            desc = f"- {tool_name}: {tool_info['description']}"
            # Add parameter info
            params = tool_info.get("parameters", {}).get("properties", {})
            if params:
                param_descs = []
                for param_name, param_info in params.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    param_descs.append(f"  {param_name} ({param_type}): {param_desc}")
                if param_descs:
                    desc += "\n" + "\n".join(param_descs)
            descriptions.append(desc)
        
        return "\n".join(descriptions)
