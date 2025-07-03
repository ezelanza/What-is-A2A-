# A2A Protocol Demo - Official Google SDK

This demo showcases the **official Google A2A (Agent-to-Agent) Protocol** using the Python SDK. It demonstrates how 4 specialized AI agents can communicate and collaborate using the standardized A2A protocol.

## 🌟 What is A2A Protocol?

The Agent-to-Agent (A2A) Protocol is an **open standard** developed by Google that enables AI agents to discover each other's capabilities and communicate seamlessly over HTTP/JSON. It solves the key challenge of interoperability in multi-agent AI systems.

### Key Benefits:
- **Standardized Communication**: All agents speak the same protocol language
- **Agent Discovery**: Agents can find and learn about each other's capabilities
- **Vendor Neutral**: Works across different AI frameworks and providers
- **Enterprise Ready**: Built-in authentication, error handling, and monitoring

## 🤖 Our A2A Agent Network

This demo creates 4 specialized agents that work together:

### 1. 🔍 Research Agent (Port 8001)
- **Specialty**: Information gathering and analysis
- **Skills**: Market analysis, trend identification, data collection
- **Use Case**: Provides comprehensive research insights

### 2. 📋 Planning Agent (Port 8002)  
- **Specialty**: Strategy and task organization
- **Skills**: Strategic planning, task breakdown, timeline creation
- **Use Case**: Creates structured plans and roadmaps

### 3. ⚙️ Technical Agent (Port 8003)
- **Specialty**: Implementation and technical solutions
- **Skills**: Architecture design, implementation, performance optimization
- **Use Case**: Provides technical expertise and solutions

### 4. ✅ Quality Agent (Port 8004)
- **Specialty**: Validation and quality assurance  
- **Skills**: Correctness validation, performance testing, compliance checking
- **Use Case**: Ensures high quality standards

## 🚀 Getting Started

### Prerequisites

1. **Python 3.12+** (required by official A2A SDK)
2. **Virtual Environment** (recommended)

### Installation

1. **Create Python 3.12 Virtual Environment**:
```bash
python3.12 -m venv a2a_env
source a2a_env/bin/activate  # On Windows: a2a_env\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

### Quick Start

Run the demo:
```bash
python a2a_demo.py
```

## 💬 Demo Interaction

When you start the demo, you'll see all 4 agents working together to provide comprehensive answers to your questions. Each agent provides its specialized perspective on your query.

### Example Questions:
- "How do I build a mobile app?"
- "What's the best way to learn AI?"
- "How can I improve team productivity?"

## 🔧 Technical Implementation

### Official A2A SDK Components Used

- **`a2a.types`**: Data structures for Agent Cards, Messages, Tasks
- **`a2a.AgentCard`**: Agent discovery and capability description
- **`a2a.Message`**: Standardized message format with messageId
- **`a2a.Task`**: Task lifecycle management with contextId

### Agent Cards

Each agent publishes an **Agent Card** containing:

```python
agent_card = a2a.AgentCard(
    name="Research Agent",
    description="Specialized in information gathering and analysis", 
    url="http://localhost:8001",
    version="1.0.0",
    capabilities=a2a.AgentCapabilities(
        streaming=False,
        pushNotifications=False
    ),
    skills=[skill_definition],
    defaultInputModes=["text"],
    defaultOutputModes=["text"]
)
```

## 🎯 Real-World Applications

This A2A pattern enables powerful use cases:

- **Enterprise Workflow Automation**: Orchestrate specialized business agents
- **AI Assistant Networks**: Combine multiple AI capabilities seamlessly  
- **Microservices for AI**: Break complex AI tasks into specialized services
- **Cross-Platform Integration**: Connect agents across different cloud providers

## 🔍 Comparison: Custom vs Official A2A

| Aspect | Custom Implementation | Official A2A SDK |
|--------|----------------------|------------------|
| Protocol Compliance | ❌ Custom format | ✅ Official standard |
| Interoperability | ❌ Limited | ✅ Universal |
| Enterprise Features | ❌ Basic | ✅ Production-ready |
| Authentication | ❌ Custom | ✅ Built-in OAuth, API keys |
| Error Handling | ❌ Ad-hoc | ✅ Standardized |
| Agent Discovery | ❌ Manual | ✅ Automatic via agent cards |

## 📚 Official Resources

- **A2A Protocol Specification**: [GitHub Repository](https://github.com/google/A2A)
- **Python SDK Documentation**: [Official Docs](https://a2aprotocol.ai/docs/guide/python-a2a.html)
- **Protocol Guide**: [A2A vs MCP Comparison](https://a2aprotocol.ai/docs/introduction/a2a-vs-mcp.html)

## 📄 License

This demo is provided under the Apache 2.0 license.

---

**Built with the Official Google A2A SDK** 🚀

*Demonstrating the future of agent interoperability*
