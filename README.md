# A2A Protocol Demo

This is a complete working implementation of the **A2A (Agent-to-Agent) Protocol**. It demonstrates how AI agents can communicate with each other using standardized JSON-RPC messages.

## What's Included

1. **`multi_agent_travel.py`** - **🌟 Multi-Agent Demo**: Four specialized agents that collaborate peer-to-peer (Travel, Calendar, Expense, Weather)
2. **`a2a_agent_server.py`** - A simple AI agent server that implements the A2A protocol
3. **`a2a_client.py`** - A client that can communicate with A2A agents
4. **`requirements.txt`** - Python dependencies

## Features Demonstrated

✅ **Multi-Agent Collaboration** - **NO SUPERVISOR NEEDED!** Four agents work together peer-to-peer  
✅ **LLM-Based Intelligence** - **NO HARDCODED RULES!** Uses real AI for understanding and routing  
✅ **Natural Language Interface** - Speak naturally, no keywords required  
✅ **Agent Discovery** - Agents find and communicate with each other automatically  
✅ **JSON-RPC Communication** - Standard A2A message format  
✅ **Task Management** - Create, monitor, and cancel tasks  
✅ **Context Continuity** - Multi-turn conversations  
✅ **Real-time Interaction** - Interactive chat sessions  
✅ **Error Handling** - Proper A2A error responses  

## 🧠 LLM-Powered Intelligence (NEW!)

**Revolutionary End-to-End AI Intelligence**

This implementation now uses **real LLM intelligence throughout the entire system** - no hardcoded responses anywhere! Every component is AI-powered:

- **Intelligent Routing** - LLM analyzes user intent and determines agent coordination
- **Dynamic Agent Responses** - Each agent uses LLM to generate contextual, intelligent responses
- **Natural Conversation** - No keywords needed, just speak naturally to any agent
- **Context-Aware Coordination** - Agents understand their roles and coordinate intelligently
- **Adaptive Personalities** - Each agent has distinct expertise and communication style
- **True A2A Spirit** - No hardcoded rules, routing, or responses anywhere in the system!

### LLM Configuration

The system supports multiple LLM providers:

```python
LLM_CONFIG = {
    "provider": "ollama",           # Options: "ollama", "openai", "anthropic"
    "model": "llama3.2:3b",        # Local model for privacy
    "base_url": "http://localhost:11434",  # Ollama URL
    "api_key": None                 # Not needed for Ollama
}
```

**Setup Options:**
1. **Ollama (Recommended)** - Free, local, private
   ```bash
   # Install Ollama: https://ollama.ai/
   ollama serve
   ollama pull llama3.2:3b
   ```

2. **OpenAI** - Requires API key
   ```bash
   pip install openai
   # Set api_key in LLM_CONFIG
   ```

3. **Anthropic Claude** - Requires API key
   ```bash
   pip install anthropic
   # Set api_key in LLM_CONFIG
   ```

**Fallback System:** If no LLM is available, the system automatically falls back to basic analysis while maintaining functionality.

## 📋 Prerequisites

### Install Ollama (Recommended - Free & Local)

**For macOS:**
```bash
# Option 1: Download from website (Easiest)
# Visit https://ollama.ai/ and download the macOS installer

# Option 2: Using Homebrew
brew install ollama
```

**For Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**For Windows:**
```bash
# Download from https://ollama.ai/ and install the Windows version
```

### Start Ollama and Install Model

```bash
# Start Ollama server (required for LLM intelligence)
ollama serve

# In another terminal, install the model
ollama pull llama3.2:3b

# Test that it's working
ollama run llama3.2:3b "Hello, are you working?"
```

**Expected Output:**
```
I'm here and ready to help. How can I assist you today?
```

**Troubleshooting Ollama:**
If you see connection errors like `Connection refused`, make sure:
- Ollama is running: `ollama serve` (keep this terminal open)
- Model is installed: `ollama pull llama3.2:3b`
- Test connectivity: `curl http://localhost:11434/api/generate -d '{"model":"llama3.2:3b","prompt":"hello","stream":false}'`

### Python Environment

```bash
# Create virtual environment
python -m venv a2a_demo

# Activate it
# On macOS/Linux:
source a2a_demo/bin/activate
# On Windows:
a2a_demo\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Test LLM Intelligence

```bash
python test_llm_intelligence.py
```

This demonstrates how the LLM analyzes natural language requests and makes intelligent routing decisions.

## 🌟 Multi-Agent Demo (Recommended)

**Four agents collaborate without a supervisor to plan your trip!**

### Run the Multi-Agent System

**Important:** Make sure you've completed the [Prerequisites](#📋-prerequisites) section first (install Ollama and Python environment).

```bash
python multi_agent_travel.py
```

**Choose from 3 modes:**
1. **Interactive Mode** - Natural language chat with intelligent agents
2. **Demo Mode** - Automated coordination demonstration  
3. **Educational Mode** - Learn A2A protocol step-by-step ⭐

## 🎓 Educational Mode (NEW!)

**See the ACTUAL A2A protocol communication in action!**

### What You'll Learn

The educational demo shows you **exactly** how A2A protocol works:

- 📡 **Agent Discovery** - How agents find each other via Agent Cards
- 📨 **JSON-RPC 2.0 Messages** - Real A2A message structure
- 🔄 **Coordination Flow** - Step-by-step multi-agent collaboration  
- 🧠 **LLM Analysis** - How AI analyzes user intent for routing
- 🎯 **A2A Nomenclature** - Proper terminology and concepts

### Run Educational Demo

**Easy way (with prerequisite checking):**
```bash
python run_educational_demo.py
```

**Direct way:**
```bash
python educational_a2a_demo.py
```

**Sample Output:**
```
🎓 EDUCATIONAL A2A PROTOCOL DEMONSTRATION
========================================================

📚 STEP 1: STARTING A2A AGENTS
   1. Starting InterfaceAgent on port 8000
      → Interface Agent - Smart routing coordinator
   2. Starting TravelAgent on port 8001
      → Travel Agent - Trip planning specialist

📚 STEP 2: A2A AGENT DISCOVERY
🔍 DISCOVERING TravelAgent...
   📡 HTTP GET → http://localhost:8001/.well-known/agent.json
   ✅ Agent Card received!
   📋 Agent Name: TravelAgent
   🔗 A2A Endpoint: http://localhost:8001/a2a/v1/
   📨 A2A Methods: message/send, tasks/get, tasks/cancel

📨 A2A MESSAGE #1
   FROM: InterfaceAgent
   TO: TravelAgent
   MESSAGE: "User request: I want to plan a business trip..."

📋 A2A JSON-RPC 2.0 MESSAGE STRUCTURE:
{
  "jsonrpc": "2.0",
  "id": "abc-123-def",
  "method": "message/send",
  "params": {
    "message": {
      "role": "agent",
      "parts": [{"kind": "text", "text": "User request..."}],
      "messageId": "msg-456",
      "contextId": "ctx-789"
    }
  }
}
```

### Educational Value

✅ **Real Protocol** - See actual A2A messages, not simulations  
✅ **Step-by-Step** - Understand each phase of agent coordination  
✅ **Clean Code** - Simple, readable implementation for learning  
✅ **Proper Terminology** - Uses official A2A nomenclature  
✅ **Interactive** - Watch agents communicate in real-time

**What you'll see:**
```
🤖 Multi-Agent A2A System Starting...
🚀 TravelAgent starting on http://localhost:8001
🚀 CalendarAgent starting on http://localhost:8002  
🚀 ExpenseAgent starting on http://localhost:8003
🚀 WeatherAgent starting on http://localhost:8004

🎭 Running Multi-Agent Trip Planning Demo...
👤 User Request: 'Book a trip to London for 3 days'

🔄 Agents collaborating...

📋 FINAL RESULT:
🛫 TRIP PLANNING COMPLETE 🛫

📅 AVAILABILITY (from Calendar Agent):
✅ April 15-17: No conflicts
✅ May 8-10: Minor meeting (moveable)

💰 BUDGET APPROVAL (from Expense Agent):  
✅ Status: APPROVED
💳 Available Budget: $5,000
📊 Estimated Cost: $2000

🌤️ WEATHER FORECAST (from Weather Agent):
🌤️ Day 1: Partly cloudy, 16°C
🌧️ Day 2: Light rain, 14°C  
☀️ Day 3: Sunny, 18°C

✅ All agents coordinated successfully! No supervisor needed!
```

**The Magic:** 
- **Travel Agent** receives your request and coordinates everything
- **Calendar Agent** checks your availability independently  
- **Expense Agent** validates budget and policy compliance
- **Weather Agent** provides forecast and packing recommendations
- **All communicate peer-to-peer** using A2A protocol - no central coordinator!

### Natural Language Examples (LLM-Powered!)

**No keywords needed! Just speak naturally:**

```bash
# Interactive mode
python multi_agent_travel.py
# Choose "Interactive" mode

# Try these natural requests:
"I'm thinking about a business trip to Tokyo next month"
"Can you help me plan a romantic getaway to Italy?"
"What's the weather like in Paris this weekend?"
"Am I free next Thursday afternoon for a meeting?"
"How much budget do I have left for travel this quarter?"
"My boss wants me to organize a team retreat with accommodation"
```

**OLD vs NEW System:**
- ❌ **OLD**: Required keywords like "plan trip", "check calendar"
- ✅ **NEW**: Natural speech like "I'm thinking about visiting somewhere warm"

- ❌ **OLD**: Hardcoded routing rules
- ✅ **NEW**: LLM intelligently decides which agents to coordinate

- ❌ **OLD**: Essentially created hidden supervisor through keyword matching
- ✅ **NEW**: True A2A peer-to-peer spirit with intelligent coordination

## Quick Start (Simple Client-Server Demo)

**Prerequisites:** Complete the [Prerequisites](#📋-prerequisites) section first.

### Start the Agent Server

In one terminal window:

```bash
python a2a_agent_server.py
```

You should see:
```
INFO:__main__:A2A Agent Server starting on http://localhost:8000
INFO:__main__:Agent Card available at: http://localhost:8000/.well-known/agent.json
INFO:__main__:A2A endpoint: http://localhost:8000/a2a/v1/
```

### Run the Client

In another terminal window:

```bash
python a2a_client.py
```

Choose from three options:
- **1. Demo conversation** - See a scripted A2A conversation
- **2. Interactive chat** - Chat with the agent yourself
- **3. Agent discovery** - Just discover the agent's capabilities

## Example Usage

### Demo Conversation Output
```
🎭 A2A Protocol Demo - Scripted Conversation
==================================================

🤖 Agent Discovery:
  Name: SimpleA2AAgent
  Description: A demonstration A2A protocol agent
  Version: 1.0.0
  Capabilities: text_processing, task_management, simple_calculations

🎬 Starting scripted conversation...

📤 Sending: Hello, are you there?
📋 Request ID: 12345-abcd-...
📊 Task Status: completed
📥 Agent Response: Hello! I'm a simple A2A agent. I can help with basic tasks, calculations, or just chat!

📤 Sending: Can you help me calculate 2+2?
📋 Request ID: 67890-efgh-...
📊 Task Status: completed
📥 Agent Response: 2 + 2 = 4
```

### Interactive Chat
```
🚀 Starting interactive A2A chat session
💡 Type 'help' for available commands, 'quit' to exit
--------------------------------------------------

You: Hello there!
📤 Sending: Hello there!
📋 Request ID: abc123...
📊 Task Status: completed
📥 Agent Response: Hello! I'm a simple A2A agent. I can help with basic tasks, calculations, or just chat!

You: What can you do?
📤 Sending: What can you do?
📋 Request ID: def456...
📊 Task Status: completed
📥 Agent Response: I can help with:
- Greetings (say hello!)
- Simple math (ask me to calculate 2+2)
- Current time
- Tell jokes
- General conversation

You: quit
👋 Goodbye!
```

## A2A Protocol Implementation Details

### Agent Discovery (Agent Card)
The agent advertises its capabilities at `/.well-known/agent.json`:

```json
{
  "schemaVersion": "0.2.0",
  "agent": {
    "name": "SimpleA2AAgent",
    "description": "A demonstration A2A protocol agent",
    "version": "1.0.0",
    "capabilities": ["text_processing", "task_management", "simple_calculations"]
  },
  "interfaces": [
    {
      "type": "a2a",
      "url": "http://localhost:8000/a2a/v1/",
      "methods": ["message/send", "tasks/get", "tasks/cancel"]
    }
  ]
}
```

### Message Format
All A2A messages use JSON-RPC 2.0 format:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Hello, agent!"
        }
      ],
      "messageId": "unique-message-id"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "result": {
    "id": "task-id",
    "contextId": "conversation-context-id",
    "status": {
      "state": "completed",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    "history": [...],
    "kind": "task"
  }
}
```

### Supported Methods

1. **`message/send`** - Send a message to the agent
2. **`tasks/get`** - Get the status of a specific task
3. **`tasks/cancel`** - Cancel a running task

### Task States

- **`submitted`** - Task has been received
- **`working`** - Task is being processed
- **`completed`** - Task finished successfully
- **`failed`** - Task encountered an error
- **`cancelled`** - Task was cancelled
- **`input-required`** - Task needs more input from user

## Testing the Protocol

### Test Agent Discovery
```bash
curl http://localhost:8000/.well-known/agent.json
```

### Test Direct A2A Message
```bash
curl -X POST http://localhost:8000/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-123",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Hello!"}],
        "messageId": "msg-123"
      }
    }
  }'
```

## Architecture

### Multi-Agent System (No Supervisor!)
```
         🌤️ Weather Agent    💰 Expense Agent
              (Port 8004)        (Port 8003)
                    ↕                ↕
                    ╰────────┬────────╯
                             │ A2A Protocol
          📅 Calendar Agent  │  🛫 Travel Agent
              (Port 8002) ←──┼──→ (Port 8001)
                             │  [Coordinator]
                    ╭────────┴────────╮
                    ↕                ↕
              👤 User Input    📋 Final Result

All agents communicate peer-to-peer using A2A JSON-RPC protocol
```

### Traditional Client-Server (Simple Demo)
```
┌─────────────────┐       A2A Protocol       ┌─────────────────┐
│   A2A Client    │ ←-------------------→    │   A2A Agent     │
│                 │   (JSON-RPC over HTTP)   │    Server       │
└─────────────────┘                          └─────────────────┘
```

## 🤖 Multi-Agent Collaboration Features

### Why This is Revolutionary:
1. **🔍 Peer-to-Peer Discovery** - Agents find each other automatically, no central registry needed
2. **🚫 No Supervisor Required** - Agents coordinate directly without a master controller  
3. **🧠 Specialized Intelligence** - Each agent is an expert in its domain
4. **🔄 Dynamic Workflow** - Travel Agent orchestrates by calling others as needed
5. **📡 Real A2A Communication** - All inter-agent messages use proper A2A protocol
6. **🔧 Modular & Scalable** - Add/remove agents without changing others

### Agent Specializations:
- **🛫 Travel Agent** → Trip planning, booking coordination  
- **📅 Calendar Agent** → Schedule management, availability checking
- **💰 Expense Agent** → Budget validation, policy compliance
- **🌤️ Weather Agent** → Forecasts, packing recommendations

### The Workflow Magic:
```
1. User: "Book trip to London"
2. Travel Agent discovers Calendar Agent 
3. Travel Agent asks: "Available dates?"
4. Calendar Agent responds with free slots
5. Travel Agent discovers Expense Agent
6. Travel Agent asks: "Budget approved for $2000?"
7. Expense Agent validates and approves
8. Travel Agent discovers Weather Agent  
9. Travel Agent asks: "London weather forecast?"
10. Weather Agent provides detailed forecast
11. Travel Agent compiles everything into final plan
```

**Result:** Complex multi-agent workflow with ZERO central coordination! 🎯

## What Makes This A2A Compliant

1. **Standardized Discovery** - Uses `/.well-known/agent.json` for agent cards
2. **JSON-RPC 2.0** - All communication follows JSON-RPC specification
3. **Proper Message Structure** - Messages have roles, parts, and metadata
4. **Task Management** - Full task lifecycle with proper states
5. **Context Continuity** - Conversations maintain context across messages
6. **Error Handling** - Standard JSON-RPC error responses
7. **🆕 Multi-Agent Orchestration** - Agents can discover and communicate with each other

## Extending the Demo

You can extend this demo by:

1. **Adding more agent capabilities** (image processing, file handling)
2. **Implementing streaming responses** with Server-Sent Events
3. **Adding authentication** with OAuth 2.0
4. **Creating multiple specialized agents** that can talk to each other
5. **Adding webhook notifications** for long-running tasks

## Protocol Specification

This implementation follows the A2A Protocol v0.2.0 specification. For the full specification, visit: https://a2aprotocol.ai

## Troubleshooting

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

**Connection refused:**
- Make sure the server is running first
- Check that the server started successfully
- Verify the URL in the client matches the server

**Import errors:**
```bash
pip install requests
```

## License

This demo code is provided as-is for educational purposes to demonstrate the A2A protocol. 