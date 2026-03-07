"""
Main entry point for Jarvis Voice Agent.

Orchestrates the three components:
1. STT Listener (speech-to-text)
2. LLM Agent (processes text)
3. MCP Server (executes actions)
"""

import logging
import sys
from listener import STTListener
from agent import LLMAgent
from mcp_server import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution loop."""
    logger.info("Starting Jarvis Voice Agent...")
    
    # Initialize components
    try:
        logger.info("Initializing STT Listener...")
        stt_listener = STTListener(model_size="base")
        stt_listener.load_model()
        
        logger.info("Initializing LLM Agent...")
        llm_agent = LLMAgent(model="qwen2.5:7b-instruct")
        
        logger.info("Initializing MCP Server...")
        mcp_server = MCPServer()
        
        logger.info("All components initialized successfully!")
        print("\n" + "="*60)
        print("Jarvis Voice Agent - Ready")
        print("="*60)
        print("\nAvailable commands:")
        print("  - Press Enter to start recording (push-to-talk)")
        print("  - Type 'quit' or 'exit' to stop")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    
    # Main loop
    try:
        while True:
            # Get user input method
            print("\n[1] Push-to-talk recording")
            print("[2] Fixed duration recording (5 seconds)")
            print("[q] Quit")
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'q' or choice == 'quit' or choice == 'exit':
                logger.info("Shutting down...")
                print("\nGoodbye!")
                break
            
            # Get transcribed text
            transcribed_text = None
            
            if choice == '1':
                transcribed_text = stt_listener.listen_push_to_talk()
            elif choice == '2':
                transcribed_text = stt_listener.listen(duration=5.0)
            else:
                print("Invalid option. Please try again.")
                continue
            
            if not transcribed_text or not transcribed_text.strip():
                print("No speech detected. Please try again.")
                continue
            
            print(f"\n[Transcribed] {transcribed_text}")
            
            # Process with LLM agent
            print("\n[Processing with LLM...]")
            llm_response = llm_agent.process(transcribed_text, include_mcp_tools=True)
            print(f"\n[LLM Response]\n{llm_response}")
            
            # Extract and execute function calls
            function_calls = llm_agent.extract_function_calls(llm_response)
            
            if function_calls:
                print(f"\n[Executing {len(function_calls)} function call(s)...]")
                for func_call in function_calls:
                    result = mcp_server.execute_function_call(func_call)
                    if result.get("success"):
                        print(f"✓ {func_call['function']} executed successfully")
                    else:
                        print(f"✗ {func_call['function']} failed: {result.get('error', 'Unknown error')}")
            else:
                print("\n[No function calls detected in response]")
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n\nShutting down...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}", exc_info=True)
        print(f"\nError: {e}")
    finally:
        logger.info("Jarvis Voice Agent stopped")


if __name__ == "__main__":
    main()
