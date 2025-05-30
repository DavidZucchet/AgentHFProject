# GAIA Benchmark Agent - Tool-Based System

This project implements a sophisticated tool-based agent system designed to tackle the GAIA benchmark challenges. The agent uses a graph-based workflow to handle complex, real-world queries that require multi-step reasoning, multimodal understanding, and proficient tool use.

## About GAIA

GAIA is a benchmark for General AI Assistants that evaluates AI systems on real-world tasks. While humans achieve ~92% success rate, current AI systems like GPT-4 with plugins only reach ~15%. This project aims to bridge that gap using an advanced agent architecture.

**Challenge Goal**: Achieve 30% or higher accuracy on GAIA benchmark questions to demonstrate effective agent capabilities.

## System Architecture

Built on **LangChain** and **LangGraph**, the system implements a sophisticated state-based workflow using **GPT-4o-mini** for optimal cost-performance balance:

### Core Components

1. **Worker Node**: 
   - Powered by GPT-4o-mini with tool binding capabilities
   - Implements iterative reasoning with configurable limits (max 10 iterations)
   - Handles multi-step task execution and file processing
   - Uses structured system prompts for consistent behavior

2. **Evaluator Node**: 
   - Structured output generation using Pydantic models
   - Formats answers according to GAIA's exact match requirements
   - Handles numeric vs. text classification automatically
   - Ensures compliance with benchmark evaluation criteria

3. **Tool Node**: 
   - LangGraph's prebuilt ToolNode for seamless tool integration
   - Automatic tool call limiting to prevent infinite loops
   - Error handling and fallback mechanisms

### Technical Stack

- **LangChain**: Framework for LLM application development
- **LangGraph**: State-based graph execution engine with memory checkpointing
- **GPT-4o-mini**: Primary reasoning engine (OpenAI)
- **Pydantic**: Structured data validation and output formatting
- **AsyncIO**: Asynchronous processing capabilities
- **MemorySaver**: Conversation state persistence across iterations

## Available Tools

- File fetching from GAIA API (`get_question_file`)
- Web search (Google Serper and DuckDuckGo)
- Wikipedia search and analysis
- Audio to text conversion
- Excel/CSV file processing
- YouTube transcript extraction
- Python script execution
- Mathematical calculations
- Plant classification
- Non-commutativity analysis

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### BasicAgent Class (Recommended)

```python
from agents import BasicAgent

# Initialize with default LangGraph configuration
agent = BasicAgent()

# Process GAIA question with structured state management
question = "What is the final numeric output from the attached Python code?"
task_id = "f918266a-b3e0-4914-865d-4faa564f1aef"
file_name = "f918266a-b3e0-4914-865d-4faa564f1aef.py"

# Execute with automatic async handling and state persistence
result = agent(question, task_id, file_name)
print(result)  # Returns cleaned final answer (no "Evaluator final answer:" prefix)
```

### Web Interface

Run the Gradio interface for interactive evaluation:

```bash
python app.py
```

Features:
- Hugging Face login integration
- Batch evaluation on multiple questions
- GAIA API integration for question retrieval and submission
- Real-time scoring and leaderboard updates

## GAIA API Integration

The system integrates with the GAIA challenge API:

- `GET /questions`: Retrieve evaluation questions
- `GET /random-question`: Fetch a single random question
- `GET /files/{task_id}`: Download task-associated files
- `POST /submit`: Submit answers for scoring

## Project Files

- `tools.py`: Tool definitions and implementations
- `agents.py`: Core agent system with worker and evaluator nodes
- `app.py`: Gradio web interface with GAIA API integration
- `requirements.txt`: Python package dependencies
- `.env`: Configuration file for API keys

## Key Technical Features

### Advanced State Management
- **TypedDict State**: Structured state management with message history, task tracking, and iteration control
- **Memory Checkpointing**: Persistent conversation state using LangGraph's MemorySaver
- **Conditional Routing**: Smart workflow routing between worker, tools, and evaluator nodes

### Robust Error Handling
- **Iteration Limiting**: Prevents infinite loops with configurable maximum iterations
- **Tool Call Limiting**: Custom callback handler to manage excessive tool usage
- **Graceful Degradation**: Continues operation even when specific tools fail

### Intelligent File Processing
- **Dynamic File Path Resolution**: Automatically retrieves correct file paths via GAIA API
- **Multi-format Support**: Handles Excel, audio, images, and text files seamlessly
- **Temporary File Management**: Automatic cleanup of processing artifacts

### Performance Optimizations
- **Async/Await Pattern**: Non-blocking operation for better responsiveness
- **UUID-based Threading**: Isolated execution contexts for concurrent requests
- **Structured Output**: Pydantic models ensure consistent response formatting

## Performance Notes

- **GPT-4o-mini**: Optimized model choice balancing capability and cost-efficiency
- **Structured Prompting**: System messages crafted for consistent GAIA benchmark performance
- **State-Based Execution**: LangGraph's StateGraph ensures reliable multi-step reasoning
- **Memory Persistence**: Conversation context maintained across tool executions
- **Exact Match Optimization**: Evaluator specifically tuned for GAIA's evaluation criteria
- **Async Architecture**: Built for scalability and concurrent request handling

Successfully completing this challenge with 30%+ accuracy demonstrates mastery of AI agent development and real-world problem-solving capabilities.
- File handling is done through temporary files that are automatically cleaned up
- The system includes iteration limiting to prevent infinite loops
- All API keys should be properly set in the `.env` file
- The system supports both synchronous and asynchronous operation
- The web interface provides a user-friendly way to interact with the system 
