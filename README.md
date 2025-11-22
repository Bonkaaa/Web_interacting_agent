# Web Interacting Agent

An intelligent web automation agent that uses LangGraph and ReAct framework to interact with websites through natural language instructions. The agent analyzes accessibility trees, makes decisions, and performs web actions to accomplish user-defined tasks.

## 🌟 Features

- **Intelligent Web Navigation**: Uses ReAct (Reasoning + Acting) framework to decide on web actions
- **Accessibility Tree Analysis**: Extracts and parses page structure for precise element identification
- **Multiple Action Types**: Supports clicking, typing, waiting, navigation, and data extraction
- **LangGraph Workflow**: Implements a state-based graph architecture for reliable task execution
- **Selenium Integration**: Browser automation with Chrome WebDriver
- **LLM-Powered Decision Making**: Uses Ollama LLM for intelligent action planning
- **Structured Output**: Pydantic models ensure type-safe agent responses

## 🏗️ Architecture

The agent follows a graph-based workflow with these key components:

1. **Driver Initialization**: Sets up Chrome WebDriver and accesses target URL
2. **Accessibility Tree Extraction**: Parses webpage structure into navigable tree
3. **ReAct Agent**: Decides next action based on task and current state
4. **Action Execution**: Performs web interactions (click, type, extract, etc.)
5. **Continue/Answer Decision**: Determines if task is complete or needs more actions
6. **Answer Generation**: Synthesizes final response from extracted data

### State Management

The agent maintains a comprehensive state including:
- Task description and messages
- WebDriver instance and URL
- Accessibility tree and node mappings
- Action history
- Extracted data from web elements
- Tool usage tracking

## 📋 Prerequisites

- Python 3.8+
- Chrome browser installed
- Ollama running locally with `gpt-oss:20b` model

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Bonkaaa/Web_interacting_agent.git
cd Web_interacting_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create `.env` file):
```bash
# Add any required API keys or configuration
```

## 📦 Dependencies

- **langgraph**: State graph framework for agent workflow
- **langchain & langchain-core**: LLM orchestration framework
- **langchain-ollama**: Ollama integration for local LLM
- **langchain_community**: Community integrations
- **langchain_huggingface**: HuggingFace model support
- **selenium**: Web browser automation
- **webdriver_manager**: Automatic ChromeDriver management
- **bs4**: BeautifulSoup4 for HTML parsing
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and structured outputs
- **torch**: PyTorch for ML operations

## 📁 Project Structure

```
Web_interacting_agent/
├── src/
│   ├── agent.py              # Main agent nodes and workflow logic
│   ├── graph.py              # LangGraph state graph definition
│   ├── tools.py              # Web interaction tools (Selenium)
│   ├── prompts.py            # Prompt templates (legacy)
│   ├── utils.py              # Logging and file utilities
│   ├── utils_agent.py        # Accessibility tree utilities
│   ├── main.ipynb            # Jupyter notebook for experimentation
│   └── components/
│       ├── answer.py         # Answer generation agent
│       ├── check_cont.py     # Continue/finish decision agent
│       ├── reAct.py          # ReAct framework implementation
│       ├── llm.py            # LLM initialization (Ollama)
│       └── template.py       # Prompt templates for agents
├── scripts/
│   └── test_graph.sh         # Shell script to test the graph
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## 💻 Usage

### Basic Usage

Run the agent with a predefined task in `graph.py`:

```bash
python -m src.graph
```

### Custom Task Example

```python
from src.graph import create_graph
from src.agent import State

# Define your task
initial_state: State = {
    "messages": [],
    "task": "Find the terms link and extract when they were published",
    "data_from_web_elements": [],
    "web_element": None,
    "url": "https://chatgpt.com",
    "driver": None,
    "accessbility_tree_str": "",
    "accessbility_node_map": {},
    "action_history": [],
    "warn_obs": [],
    "action": [],
    "tool_count": 0,
    "max_tool_usage": 10,
    "final_anwser": "",
}

# Create and run the graph
graph = create_graph()
final_state = graph.invoke(initial_state)
print("Final Answer:", final_state["final_anwser"])
```

### Testing with Shell Script

```bash
cd scripts
./test_graph.sh
```

## 🔧 Available Actions

The agent can perform the following web interactions:

- **Click**: `execute_click_action` - Click on web elements
- **Type**: `execute_type_action` - Type text into input fields
- **Wait**: `execute_wait_action` - Wait for page loading
- **Go Back**: `execute_go_back_action` - Navigate to previous page
- **Go Home**: `execute_go_home_action` - Navigate to Google homepage
- **Extract Data**: `extract_data_from_element` - Extract text content from elements

## 🧪 Testing

The project includes test tasks in `graph.py`:

```python
# Click testing
"task": "Click on the Terms link at the bottom of the page"

# Type testing
"task": "Type 'Hello, Chatgpt' into the text box"

# Wait testing
"task": "Wait for 5 seconds"

# Real-world task
"task": "Find the terms link and find out when the terms are published"
```

## 📊 Logging

Logs are automatically created in the `logs/` directory:
- `new_agent.log` - Main agent execution logs
- `tools.log` - Web interaction tool logs
- `utils_agent.log` - Utility function logs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Known Issues

- The `type_node` function is marked as "NEED DEBUGGING" in agent.py
- Maximum tool usage is limited to prevent infinite loops
- Chrome WebDriver needs to be compatible with installed Chrome version
- The codebase contains some typos: `final_anwser` (should be `final_answer`) and `accessbility` (should be `accessibility`)
- The requirements.txt file contains `langchain-ollama` twice (duplicate entry)

## 🔮 Future Improvements

- Support for multiple browser types (Firefox, Edge)
- Enhanced error recovery mechanisms
- Screenshot capabilities for visual verification
- Support for more complex web interactions (drag-and-drop, file uploads)
- Integration with more LLM providers
- Improved accessibility tree filtering for better performance

## 📧 Contact

For questions or support, please open an issue on GitHub." 
