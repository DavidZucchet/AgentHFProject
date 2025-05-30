# Agent Tools and Graph System

This project implements a sophisticated tool-based agent system with a graph-based workflow, designed to handle various types of queries and tasks using multiple tools and evaluation steps.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Files

- `tools.py`: Contains all the tool definitions used by the agents
- `agents.py`: Implements the agent system with worker and evaluator nodes
- `app.py`: Gradio web interface for running the agent system
- `requirements.txt`: Lists all required Python packages
- `.env`: Configuration file for API keys (create this file)

## Usage

### Using the BasicAgent Class

The recommended way to use the agent system is through the `BasicAgent` class:

```python
from agents import BasicAgent

# Initialize the agent
agent = BasicAgent()

# Process a question
question = "What is the final numeric output from the attached Python code?"
task_id = "f918266a-b3e0-4914-865d-4faa564f1aef"
file_name = "f918266a-b3e0-4914-865d-4faa564f1aef.py"  # Leave empty if not needed

# Get the result
result = agent(question, task_id, file_name)
print(result)
```

### Running the Web Interface

You can also use the Gradio web interface:

```bash
python app.py
```

This will start a web server where you can:
1. Log in with your Hugging Face account
2. Run evaluations on multiple questions
3. View results and scores

## Available Tools

The system includes the following tools:
- File fetching from API (`get_question_file`)
- Web search (Google Serper and DuckDuckGo)
- Non-commutativity analysis
- Wikipedia search
- Audio to text conversion
- Excel file processing
- YouTube transcript extraction
- Python script execution
- Sum calculation for selected items
- Plant part classification

## System Architecture

The system uses a graph-based workflow with the following components:

1. **Worker Node**: Processes questions using available tools
   - Uses GPT-4 for reasoning and tool selection
   - Implements iteration limiting to prevent infinite loops
   - Handles file operations and tool execution

2. **Evaluator Node**: Assesses responses and formats final answers
   - Determines if the answer is numeric or text-based
   - Formats the final answer according to specific rules
   - Handles different answer types (numbers, strings, lists)

3. **Tool Node**: Manages tool execution and results

## Notes

- The system uses GPT-4 for both worker and evaluator agents
- File handling is done through temporary files that are automatically cleaned up
- The system includes iteration limiting to prevent infinite loops
- All API keys should be properly set in the `.env` file
- The system supports both synchronous and asynchronous operation
- The web interface provides a user-friendly way to interact with the system 
