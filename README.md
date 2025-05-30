# GAIA Benchmark Agent - Tool-Based System

This project implements a sophisticated tool-based agent system designed to tackle the GAIA benchmark challenges. The agent uses a graph-based workflow to handle complex, real-world queries that require multi-step reasoning, multimodal understanding, and proficient tool use.

## About GAIA

GAIA is a benchmark for General AI Assistants that evaluates AI systems on real-world tasks. While humans achieve ~92% success rate, current AI systems like GPT-4 with plugins only reach ~15%. This project aims to bridge that gap using an advanced agent architecture.

**Challenge Goal**: Achieve 30% or higher accuracy on GAIA benchmark questions to demonstrate effective agent capabilities.

## System Architecture

The system uses a graph-based workflow with three main components:

1. **Worker Node**: Processes questions using available tools with GPT-4 reasoning
2. **Evaluator Node**: Assesses responses and formats final answers according to GAIA requirements
3. **Tool Node**: Manages execution of specialized tools for different task types

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

# Initialize the agent
agent = BasicAgent()

# Process a GAIA question
question = "What is the final numeric output from the attached Python code?"
task_id = "f918266a-b3e0-4914-865d-4faa564f1aef"
file_name = "f918266a-b3e0-4914-865d-4faa564f1aef.py"

# Get the result
result = agent(question, task_id, file_name)
print(result)
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

## Key Features

- **Iteration Control**: Prevents infinite loops with smart iteration limiting
- **Multimodal Support**: Handles text, images, audio, and structured data
- **Exact Match Evaluation**: Answers formatted to match GAIA's exact requirements
- **Automatic Cleanup**: Temporary files are automatically managed
- **Error Handling**: Robust error handling for tool failures and API issues

## Performance Notes

- Uses GPT-4 for optimal reasoning capabilities
- Implements smart tool selection based on question analysis
- Supports both synchronous and asynchronous operations
- Optimized for GAIA's exact match evaluation criteria

Successfully completing this challenge with 30%+ accuracy demonstrates mastery of AI agent development and real-world problem-solving capabilities.
- File handling is done through temporary files that are automatically cleaned up
- The system includes iteration limiting to prevent infinite loops
- All API keys should be properly set in the `.env` file
- The system supports both synchronous and asynchronous operation
- The web interface provides a user-friendly way to interact with the system 
