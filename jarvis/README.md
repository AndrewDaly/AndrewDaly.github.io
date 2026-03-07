# Jarvis Voice Agent

A three-part voice agent system that listens to speech, processes it with an LLM, and executes actions via MCP (Model Context Protocol).

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Microphone│────▶│  STT Listener│────▶│  LLM Agent  │────▶│  MCP Server │
│   (Audio)   │     │   (Whisper)  │     │  (Ollama)   │     │  (Functions)│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                                                                    ▼
                                                           ┌─────────────┐
                                                           │   Actions   │
                                                           │  (Print/etc)│
                                                           └─────────────┘
```

## Components

### 1. STT Listener (`src/listener/stt_listener.py`)
- Uses OpenAI Whisper for speech-to-text transcription
- Captures audio from microphone using `sounddevice`
- Supports push-to-talk and fixed-duration recording modes
- Configurable Whisper model size (tiny, base, small, medium, large)

### 2. LLM Agent (`src/agent/llm_agent.py`)
- Processes transcribed text using Ollama (similar to `ai_agent_orchestration` examples)
- Uses `qwen2.5:7b-instruct` model by default
- Extracts function calls from LLM responses
- Includes MCP tool descriptions in prompts

### 3. MCP Server (`src/mcp_server/`)
- Exposes Python functions as tools the LLM can call
- Currently implements `print_action(message: str)` function
- Can be extended with additional tools

## Setup

### Prerequisites

1. **Python 3.11+** (tested with Python 3.11.0)
2. **Ollama** - Install from [ollama.ai](https://ollama.ai)
   - After installation, pull the model: `ollama pull qwen2.5:7b-instruct`
3. **Microphone** - Working microphone for audio input

### Installation

1. Navigate to the jarvis directory:
```bash
cd jarvis
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify Ollama is installed and the model is available:
```bash
ollama list
# Should show qwen2.5:7b-instruct or similar
```

## Usage

### Running the Agent

```bash
python src/main.py
```

### Interaction Modes

1. **Push-to-talk**: Press Enter to start recording, then Enter again to stop
2. **Fixed duration**: Record for a fixed 5-second duration

### Example Flow

1. Start the application
2. Select recording mode (1 or 2)
3. Speak into your microphone
4. The system will:
   - Transcribe your speech to text
   - Send it to the LLM for processing
   - Execute any function calls the LLM decides to make
   - Display the results

### Example Interaction

```
[1] Push-to-talk recording
[2] Fixed duration recording (5 seconds)
[q] Quit

Select option: 1

Press Enter to start recording...
Recording... (Press Enter to stop)
[User speaks: "Hello, please print a greeting message"]

[Transcribed] Hello, please print a greeting message

[Processing with LLM...]

[LLM Response]
I'll print a greeting message for you.
TOOL:print_action("Hello! Welcome to Jarvis Voice Agent!")

[Executing 1 function call(s)...]
[ACTION] Hello! Welcome to Jarvis Voice Agent!
✓ print_action executed successfully
```

## Configuration

### Whisper Model Size

Edit `src/main.py` to change the Whisper model:
```python
stt_listener = STTListener(model_size="base")  # Options: tiny, base, small, medium, large
```

- **tiny**: Fastest, least accurate
- **base**: Good balance (default)
- **small**: Better accuracy
- **medium/large**: Best accuracy, slower

### Ollama Model

Edit `src/main.py` to change the LLM model:
```python
llm_agent = LLMAgent(model="qwen2.5:7b-instruct")  # Change to your preferred model
```

## Project Structure

```
jarvis/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main entry point
│   ├── listener/
│   │   ├── __init__.py
│   │   └── stt_listener.py        # Whisper-based STT
│   ├── agent/
│   │   ├── __init__.py
│   │   └── llm_agent.py           # Ollama LLM integration
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py               # MCP server implementation
│       └── tools.py                # Python functions exposed via MCP
├── requirements.txt
└── README.md
```

## Adding New MCP Tools

To add a new tool that the LLM can call:

1. Add the function to `src/mcp_server/tools.py`:
```python
def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Description of what this tool does."""
    # Your implementation
    return {"success": True, "result": "..."}
```

2. Register it in `AVAILABLE_TOOLS`:
```python
AVAILABLE_TOOLS = {
    # ... existing tools ...
    "my_new_tool": {
        "function": my_new_tool,
        "description": "Description for the LLM",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."},
                "param2": {"type": "integer", "description": "..."}
            },
            "required": ["param1", "param2"]
        }
    }
}
```

3. The LLM will automatically be aware of the new tool in its prompts.

## Troubleshooting

### "Ollama not found"
- Ensure Ollama is installed and in your PATH
- Test with: `ollama --version`
- On Windows, you may need to restart your terminal after installation

### "No module named 'whisper'"
- Install dependencies: `pip install -r requirements.txt`
- If using a virtual environment, ensure it's activated

### "No audio input detected"
- Check microphone permissions
- Verify microphone is working in other applications
- On Windows, check Sound settings
- Try a different audio device if available

### "Model not found" (Whisper)
- Whisper models are downloaded automatically on first use
- Ensure you have internet connection for first run
- Models are cached in `~/.cache/whisper/`

### Poor transcription accuracy
- Try a larger Whisper model (small, medium, or large)
- Ensure good microphone quality and quiet environment
- Speak clearly and at a normal pace

## Future Enhancements

- [ ] Voice Activity Detection (VAD) for automatic recording
- [ ] Text-to-Speech (TTS) output for LLM responses
- [ ] More MCP tools (file operations, web search, etc.)
- [ ] Configuration file for settings
- [ ] Better error handling and recovery
- [ ] Streaming transcription for real-time feedback
- [ ] Multiple language support

## License

Part of Andrew Daly's portfolio projects.
