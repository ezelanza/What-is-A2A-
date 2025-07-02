# A2A Protocol Demo

This is a complete working implementation of the **A2A (Agent-to-Agent) Protocol** developed by Google. It demonstrates how AI agents can communicate with each other using standardized JSON-RPC messages.

## What's Included

1. **`a2a_agent_server.py`** - A simple AI agent server that implements the A2A protocol
2. **`a2a_client.py`** - A client that can communicate with A2A agents
3. **`requirements.txt`** - Python dependencies

## Features Demonstrated

✅ **Agent Discovery** - Find agents and their capabilities  
✅ **JSON-RPC Communication** - Standard A2A message format  
✅ **Task Management** - Create, monitor, and cancel tasks  
✅ **Context Continuity** - Multi-turn conversations  
✅ **Real-time Interaction** - Interactive chat sessions  
✅ **Error Handling** - Proper A2A error responses  

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Agent Server

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

### 3. Run the Client

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

```
┌─────────────────┐       A2A Protocol       ┌─────────────────┐
│                 │   (JSON-RPC over HTTP)   │                 │
│   A2A Client    │ ←-------------------→    │   A2A Agent     │
│                 │                          │    Server       │
└─────────────────┘                          └─────────────────┘
        │                                             │
        │                                             │
        ▼                                             ▼
┌─────────────────┐                          ┌─────────────────┐
│ • Agent Discovery│                          │ • Task Manager  │
│ • Message Sending│                          │ • AI Processing │
│ • Task Monitoring│                          │ • Context Mgmt  │
└─────────────────┘                          └─────────────────┘
```

## What Makes This A2A Compliant

1. **Standardized Discovery** - Uses `/.well-known/agent.json` for agent cards
2. **JSON-RPC 2.0** - All communication follows JSON-RPC specification
3. **Proper Message Structure** - Messages have roles, parts, and metadata
4. **Task Management** - Full task lifecycle with proper states
5. **Context Continuity** - Conversations maintain context across messages
6. **Error Handling** - Standard JSON-RPC error responses

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