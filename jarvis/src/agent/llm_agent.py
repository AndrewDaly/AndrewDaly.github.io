"""
LLM Agent using Ollama for processing transcribed text.

Follows the pattern from ai_agent_orchestration examples.
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLMAgent:
    """LLM Agent that processes text using Ollama."""
    
    def __init__(self, model: str = "qwen2.5:7b-instruct"):
        """
        Initialize the LLM agent.
        
        Args:
            model: Ollama model name (default: qwen2.5:7b-instruct)
        """
        self.model = model
        logger.info(f"Initializing LLM agent with model: {model}")
    
    def run_ollama(self, prompt_text: str) -> str:
        """
        Run Ollama with the given prompt.
        
        Args:
            prompt_text: The prompt to send to Ollama
            
        Returns:
            The response from Ollama
        """
        try:
            logger.info(f"Sending prompt to Ollama ({self.model})...")
            result = subprocess.run(
                ["ollama", "run", self.model, prompt_text],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )
            response = result.stdout.strip()
            logger.info(f"Received response from Ollama")
            return response
        except subprocess.CalledProcessError as e:
            error_msg = f"Error running Ollama: {e.stderr}"
            logger.error(error_msg)
            return error_msg
        except FileNotFoundError:
            error_msg = "Ollama not found. Please ensure Ollama is installed and in PATH."
            logger.error(error_msg)
            return error_msg
    
    def process(self, text: str, include_mcp_tools: bool = True) -> str:
        """
        Process transcribed text through the LLM.
        
        Args:
            text: The transcribed text from STT
            include_mcp_tools: Whether to include MCP tool descriptions in prompt
            
        Returns:
            LLM response
        """
        # Build prompt with MCP tool information if needed
        if include_mcp_tools:
            prompt = f"""You are Jarvis, a helpful AI assistant. The user said: "{text}"

Available tools you can use:
- print_action(message: str): Prints a message to the console. Use this when you want to output information or confirm actions.

Respond naturally to the user's input. If you need to use a tool, format it as: TOOL:print_action("your message here")

User input: {text}
"""
        else:
            prompt = f"""You are Jarvis, a helpful AI assistant. The user said: "{text}"

Respond naturally to the user's input.

User input: {text}
"""
        
        return self.run_ollama(prompt)
    
    def extract_function_calls(self, response: str) -> list:
        """
        Extract function calls from LLM response.
        
        Looks for patterns like: TOOL:print_action("message")
        
        Args:
            response: The LLM response text
            
        Returns:
            List of function calls, each as a dict with 'function' and 'args'
        """
        function_calls = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('TOOL:'):
                # Parse TOOL:function_name("arg1", "arg2")
                try:
                    tool_part = line[5:].strip()  # Remove 'TOOL:'
                    if '(' in tool_part and ')' in tool_part:
                        func_name = tool_part.split('(')[0].strip()
                        args_str = tool_part.split('(', 1)[1].rsplit(')', 1)[0]
                        
                        # Simple parsing for string arguments
                        import re
                        args = re.findall(r'"([^"]*)"', args_str)
                        
                        function_calls.append({
                            'function': func_name,
                            'args': args
                        })
                except Exception as e:
                    logger.warning(f"Failed to parse function call: {line}, error: {e}")
        
        return function_calls
