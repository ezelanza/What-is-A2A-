#!/usr/bin/env python3
"""
A2A Protocol Client Implementation
Demonstrates how to communicate with an A2A agent using the protocol.
"""

import json
import uuid
import requests
import time
from datetime import datetime

class A2AClient:
    """A2A Protocol Client for communicating with agents"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_context_id = None
        self.current_task_id = None
    
    def discover_agent(self):
        """Discover agent capabilities through Agent Card"""
        try:
            response = self.session.get(f"{self.base_url}/.well-known/agent.json")
            response.raise_for_status()
            agent_card = response.json()
            
            print("🤖 Agent Discovery:")
            print(f"  Name: {agent_card['agent']['name']}")
            print(f"  Description: {agent_card['agent']['description']}")
            print(f"  Version: {agent_card['agent']['version']}")
            print(f"  Capabilities: {', '.join(agent_card['agent']['capabilities'])}")
            print()
            
            return agent_card
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to discover agent: {e}")
            return None
    
    def send_message(self, text, context_id=None, task_id=None):
        """Send a message to the agent using A2A protocol"""
        
        # Create message structure
        message = {
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": text
                }
            ],
            "messageId": str(uuid.uuid4())
        }
        
        # Add context and task IDs if provided
        if context_id:
            message["contextId"] = context_id
        if task_id:
            message["taskId"] = task_id
        
        # Create JSON-RPC request
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": message,
                "metadata": {}
            }
        }
        
        print(f"📤 Sending: {text}")
        print(f"📋 Request ID: {request_data['id']}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/a2a/v1/",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error: {result['error']['message']}")
                return None
            
            task = result.get("result", {})
            
            # Store context and task IDs for conversation continuity
            self.current_context_id = task.get("contextId")
            self.current_task_id = task.get("id")
            
            # Extract agent response
            status = task.get("status", {})
            print(f"📊 Task Status: {status.get('state')}")
            
            if status.get("state") == "completed":
                # Look for agent response in history
                history = task.get("history", [])
                for message in reversed(history):
                    if message.get("role") == "agent":
                        for part in message.get("parts", []):
                            if part.get("kind") == "text":
                                print(f"📥 Agent Response: {part.get('text')}")
                                print()
                                return task
            
            elif status.get("state") == "input-required":
                # Agent needs more input
                status_message = status.get("message", {})
                for part in status_message.get("parts", []):
                    if part.get("kind") == "text":
                        print(f"❓ Agent asks: {part.get('text')}")
                        print()
                        return task
            
            else:
                print(f"⏳ Task in progress: {status.get('state')}")
                print()
                return task
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send message: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse response: {e}")
            return None
    
    def get_task(self, task_id):
        """Get task status"""
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/get",
            "params": {
                "id": task_id
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/a2a/v1/",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error getting task: {result['error']['message']}")
                return None
            
            return result.get("result")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get task: {e}")
            return None
    
    def cancel_task(self, task_id):
        """Cancel a task"""
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/cancel",
            "params": {
                "id": task_id
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/a2a/v1/",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"❌ Error cancelling task: {result['error']['message']}")
                return None
            
            print("✅ Task cancelled successfully")
            return result.get("result")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to cancel task: {e}")
            return None
    
    def interactive_chat(self):
        """Start an interactive chat session"""
        print("🚀 Starting interactive A2A chat session")
        print("💡 Type 'help' for available commands, 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'new':
                    self.current_context_id = None
                    self.current_task_id = None
                    print("🆕 Started new conversation")
                    continue
                
                if user_input.lower().startswith('task '):
                    task_id = user_input[5:].strip()
                    task = self.get_task(task_id)
                    if task:
                        print(f"📋 Task {task_id}:")
                        print(f"   Status: {task.get('status', {}).get('state')}")
                        print(f"   Context: {task.get('contextId')}")
                    continue
                
                # Send message with context continuity
                self.send_message(
                    user_input, 
                    context_id=self.current_context_id,
                    task_id=self.current_task_id if user_input.lower() != 'new' else None
                )
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break

def demo_conversation():
    """Demonstrate A2A protocol with a scripted conversation"""
    print("🎭 A2A Protocol Demo - Scripted Conversation")
    print("=" * 50)
    
    client = A2AClient()
    
    # Discover the agent
    agent_card = client.discover_agent()
    if not agent_card:
        print("❌ Cannot continue without agent discovery")
        return
    
    # Demo conversation
    demo_messages = [
        "Hello, are you there?",
        "Can you help me calculate 2+2?",
        "What time is it?",
        "Tell me a joke",
        "Can you help me with math problems?",
        "Calculate 10*5",
        "Thanks for your help!"
    ]
    
    print("🎬 Starting scripted conversation...")
    print()
    
    for message in demo_messages:
        client.send_message(message, context_id=client.current_context_id)
        time.sleep(1)  # Small delay for readability
    
    print("✅ Demo conversation completed!")

def main():
    """Main function - choose demo mode or interactive mode"""
    print("🤖 A2A Protocol Client")
    print("Choose mode:")
    print("1. Demo conversation (scripted)")
    print("2. Interactive chat")
    print("3. Agent discovery only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        demo_conversation()
    elif choice == "2":
        client = A2AClient()
        # First discover the agent
        agent_card = client.discover_agent()
        if agent_card:
            client.interactive_chat()
        else:
            print("❌ Cannot start chat without agent discovery")
    elif choice == "3":
        client = A2AClient()
        client.discover_agent()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 