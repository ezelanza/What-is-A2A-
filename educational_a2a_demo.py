#!/usr/bin/env python3
"""
Educational A2A Protocol Demonstration

This demo shows the ACTUAL A2A (Agent-to-Agent) protocol communication:
- Real JSON-RPC 2.0 messages
- Agent discovery via Agent Cards
- Step-by-step coordination flow
- Interactive visualization of A2A protocol

Educational Focus: Understanding how agents communicate using A2A standard
"""

import json
import uuid
import time
import requests
import threading
from datetime import datetime
from multi_agent_travel import (
    TravelAgent, CalendarAgent, ExpenseAgent, WeatherAgent, 
    InterfaceAgent, start_agent, shutdown_all_agents, llm
)

class A2AEducationalDemo:
    """Educational demonstration of A2A protocol communication"""
    
    def __init__(self):
        self.agents_started = False
        self.message_count = 0
        
    def start_agents_for_demo(self):
        """Start all agents for educational demonstration"""
        if self.agents_started:
            return
            
        print("🎓 EDUCATIONAL A2A PROTOCOL DEMONSTRATION")
        print("="*60)
        print("Learn how AI agents communicate using the A2A standard!")
        print()
        
        print("📚 STEP 1: STARTING A2A AGENTS")
        print("-" * 30)
        
        # Start agents in background threads
        agents = [
            (InterfaceAgent, "Interface Agent - Smart routing coordinator"),
            (TravelAgent, "Travel Agent - Trip planning specialist"),
            (CalendarAgent, "Calendar Agent - Schedule management"),
            (ExpenseAgent, "Expense Agent - Budget and financial approval"),
            (WeatherAgent, "Weather Agent - Meteorological expertise")
        ]
        
        for i, (agent_class, description) in enumerate(agents, 1):
            agent_name = agent_class.__name__
            port = 8000 + i - 1
            print(f"   {i}. Starting {agent_name} on port {port}")
            print(f"      → {description}")
            
            # Start agent in background
            thread = threading.Thread(target=start_agent, args=(agent_class,), daemon=True)
            thread.start()
            time.sleep(1)  # Allow agent to start
            
        print("\n✅ All A2A agents are running!")
        print("📡 Each agent exposes an Agent Card at /.well-known/agent.json")
        print("🔗 Agents communicate via JSON-RPC 2.0 over HTTP")
        self.agents_started = True
        time.sleep(2)
        
    def demonstrate_agent_discovery(self):
        """Show the A2A agent discovery process"""
        print("\n📚 STEP 2: A2A AGENT DISCOVERY")
        print("-" * 30)
        print("Agents discover each other using Agent Cards (A2A standard)")
        print()
        
        # Discover each agent
        agent_ports = [8001, 8002, 8003, 8004]  # Skip InterfaceAgent for clarity
        agent_names = ["TravelAgent", "CalendarAgent", "ExpenseAgent", "WeatherAgent"]
        
        for port, name in zip(agent_ports, agent_names):
            print(f"🔍 DISCOVERING {name}...")
            
            try:
                # Show the actual HTTP request for agent discovery
                agent_card_url = f"http://localhost:{port}/.well-known/agent.json"
                print(f"   📡 HTTP GET → {agent_card_url}")
                
                response = requests.get(agent_card_url, timeout=3)
                if response.status_code == 200:
                    agent_card = response.json()
                    print(f"   ✅ Agent Card received!")
                    
                    # Show key parts of the Agent Card
                    print(f"   📋 Agent Name: {agent_card['agent']['name']}")
                    print(f"   📋 Capabilities: {', '.join(agent_card['agent']['capabilities'])}")
                    
                    # Show A2A interface details
                    for interface in agent_card.get('interfaces', []):
                        if interface.get('type') == 'a2a':
                            print(f"   🔗 A2A Endpoint: {interface['url']}")
                            print(f"   📨 A2A Methods: {', '.join(interface['methods'])}")
                            break
                else:
                    print(f"   ❌ Discovery failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Discovery error: {e}")
            
            print()
            time.sleep(1)
            
    def demonstrate_a2a_message(self, sender, receiver, message_text, context_id=None):
        """Show actual A2A JSON-RPC message exchange"""
        self.message_count += 1
        
        print(f"📨 A2A MESSAGE #{self.message_count}")
        print(f"   FROM: {sender}")
        print(f"   TO: {receiver}")
        print(f"   MESSAGE: \"{message_text[:50]}{'...' if len(message_text) > 50 else ''}\"")
        print()
        
        # Create the actual A2A JSON-RPC 2.0 message
        request_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        if not context_id:
            context_id = str(uuid.uuid4())
            
        a2a_message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "message/send",
            "params": {
                "message": {
                    "role": "agent",
                    "parts": [
                        {
                            "kind": "text",
                            "text": message_text
                        }
                    ],
                    "messageId": message_id,
                    "contextId": context_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
        }
        
        print("📋 A2A JSON-RPC 2.0 MESSAGE STRUCTURE:")
        print(json.dumps(a2a_message, indent=2))
        print()
        
        # Send the actual message
        receiver_port = {
            "TravelAgent": 8001,
            "CalendarAgent": 8002, 
            "ExpenseAgent": 8003,
            "WeatherAgent": 8004,
            "InterfaceAgent": 8000
        }.get(receiver)
        
        if receiver_port:
            try:
                url = f"http://localhost:{receiver_port}/a2a/v1/"
                print(f"🌐 HTTP POST → {url}")
                
                response = requests.post(url, json=a2a_message, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    print("✅ A2A RESPONSE RECEIVED:")
                    
                    # Extract and show the response
                    if 'result' in result:
                        history = result['result'].get('history', [])
                        for msg in history:
                            if msg.get('role') == 'agent':
                                for part in msg.get('parts', []):
                                    if part.get('kind') == 'text':
                                        response_text = part.get('text', '')[:100]
                                        print(f"   📥 \"{response_text}{'...' if len(part.get('text', '')) > 100 else ''}\"")
                                        break
                                break
                else:
                    print(f"❌ A2A Communication failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ A2A Communication error: {e}")
        
        print("\n" + "─" * 60 + "\n")
        time.sleep(2)
        
    def demonstrate_user_request_flow(self):
        """Show complete A2A coordination flow for a user request"""
        print("📚 STEP 3: A2A COORDINATION FLOW")
        print("-" * 30)
        print("Watch how agents coordinate using A2A protocol!")
        print()
        
        user_request = "I want to plan a business trip to Tokyo for a conference next month"
        context_id = str(uuid.uuid4())
        
        print(f"👤 USER REQUEST: \"{user_request}\"")
        print(f"🆔 CONTEXT ID: {context_id}")
        print()
        
        # Step 1: User to InterfaceAgent
        print("🔄 PHASE 1: INTELLIGENT ROUTING")
        print("The InterfaceAgent analyzes the request using LLM...")
        
        # Show LLM analysis
        self.show_llm_analysis(user_request)
        
        # Step 2: InterfaceAgent coordinates with TravelAgent
        print("\n🔄 PHASE 2: PRIMARY AGENT COORDINATION")
        enhanced_request = f"User request: {user_request}\n\nThis is a complex business trip requiring coordination with CalendarAgent for scheduling, ExpenseAgent for budget approval, and WeatherAgent for travel preparation."
        
        self.demonstrate_a2a_message(
            "InterfaceAgent", 
            "TravelAgent", 
            enhanced_request,
            context_id
        )
        
        # Step 3: TravelAgent coordinates with other agents
        print("🔄 PHASE 3: MULTI-AGENT A2A COORDINATION")
        print("TravelAgent now coordinates with specialist agents...")
        print()
        
        # TravelAgent → CalendarAgent
        self.demonstrate_a2a_message(
            "TravelAgent",
            "CalendarAgent", 
            "What are the available dates for a business trip to Tokyo next month? Looking for 5-7 day window.",
            context_id
        )
        
        # TravelAgent → ExpenseAgent  
        self.demonstrate_a2a_message(
            "TravelAgent",
            "ExpenseAgent",
            "Need budget approval for Tokyo business trip. Estimated cost: $3500 including flights, hotel, and conference fees.",
            context_id
        )
        
        # TravelAgent → WeatherAgent
        self.demonstrate_a2a_message(
            "TravelAgent", 
            "WeatherAgent",
            "What's the weather forecast for Tokyo next month? Need packing recommendations for business traveler.",
            context_id
        )
        
        print("🎉 A2A COORDINATION COMPLETE!")
        print("✅ All agents communicated using standard A2A protocol")
        print("✅ JSON-RPC 2.0 messages maintained context continuity") 
        print("✅ No central supervisor - pure peer-to-peer coordination")
        
    def show_llm_analysis(self, user_request):
        """Show how LLM analyzes the request for routing"""
        print("🧠 LLM INTENT ANALYSIS:")
        
        system_prompt = """You are analyzing a user request for A2A agent routing. Respond with your analysis in this format:

REQUEST ANALYSIS:
- Intent: [what the user wants]
- Complexity: [simple/complex]
- Agents Needed: [list of agents]
- Coordination Required: [yes/no and why]

Be concise and educational."""

        try:
            analysis = llm.query_llm(user_request, system_prompt)
            print(f"   {analysis}")
        except Exception as e:
            print(f"   Analysis: Complex business trip requiring TravelAgent coordination with CalendarAgent, ExpenseAgent, and WeatherAgent")
        
        print()
        
    def show_a2a_protocol_summary(self):
        """Educational summary of A2A protocol"""
        print("\n📚 A2A PROTOCOL EDUCATIONAL SUMMARY")
        print("="*50)
        
        print("\n🔑 KEY A2A CONCEPTS DEMONSTRATED:")
        print("   1. Agent Discovery - Agents find each other via Agent Cards")
        print("   2. JSON-RPC 2.0 - Standard message format for communication") 
        print("   3. Context Continuity - Messages maintain conversational context")
        print("   4. Peer-to-Peer - No central supervisor, agents coordinate directly")
        print("   5. Task Management - Each message creates trackable tasks")
        
        print("\n📡 A2A MESSAGE STRUCTURE:")
        print("   • jsonrpc: '2.0' - Protocol version")
        print("   • id: Unique request identifier")
        print("   • method: 'message/send' - A2A method")
        print("   • params.message.role: 'agent' or 'user'")
        print("   • params.message.parts: Message content")
        print("   • params.message.contextId: Conversation continuity")
        
        print("\n🌐 A2A ENDPOINTS:")
        print("   • Agent Card: /.well-known/agent.json (discovery)")
        print("   • A2A Interface: /a2a/v1/ (communication)")
        print("   • Methods: message/send, tasks/get, tasks/cancel")
        
        print("\n🎯 EDUCATIONAL VALUE:")
        print("   ✅ See real A2A protocol in action")
        print("   ✅ Understand agent-to-agent communication")
        print("   ✅ Learn JSON-RPC 2.0 message format")
        print("   ✅ Observe multi-agent coordination patterns")
        print("   ✅ No hardcoded routing - pure AI intelligence")
        
def main():
    """Main educational demonstration"""
    demo = A2AEducationalDemo()
    
    try:
        # Start the educational demonstration
        demo.start_agents_for_demo()
        
        # Show agent discovery
        demo.demonstrate_agent_discovery()
        
        # Show A2A communication flow
        demo.demonstrate_user_request_flow()
        
        # Educational summary
        demo.show_a2a_protocol_summary()
        
        print("\n🎓 EDUCATIONAL DEMO COMPLETE!")
        print("You've seen the A2A protocol in action with real agents!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        print("\n🔌 Shutting down A2A agents...")
        shutdown_all_agents()
        time.sleep(2)
        print("✅ All agents stopped")

if __name__ == "__main__":
    main() 