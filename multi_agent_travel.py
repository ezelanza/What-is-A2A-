#!/usr/bin/env python3
"""
Multi-Agent A2A System Demo
Four specialized agents that collaborate peer-to-peer without a supervisor:
- Travel Agent: Coordinates trip planning
- Calendar Agent: Manages schedules and availability  
- Expense Agent: Handles budgets and cost validation
- Weather Agent: Provides weather forecasts and recommendations
"""

import json
import uuid
import time
import requests
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AgentRegistry:
    """Registry for agents to discover each other"""
    def __init__(self):
        self.agents = {}
    
    def register(self, name, url):
        self.agents[name] = url
        
    def discover(self, name):
        return self.agents.get(name)
    
    def list_agents(self):
        return self.agents

# Global registry for agent discovery
registry = AgentRegistry()

class A2AAgent:
    """Base class for A2A agents"""
    
    def __init__(self, name, port, capabilities):
        self.name = name
        self.port = port
        self.capabilities = capabilities
        self.base_url = f"http://localhost:{port}"
        self.logger = logging.getLogger(name)
        self.tasks = {}
        self.contexts = {}
        
        # Register with discovery service
        registry.register(name, self.base_url)
    
    def discover_agent(self, agent_name):
        """Discover another agent's endpoint"""
        agent_url = registry.discover(agent_name)
        if not agent_url:
            return None
            
        try:
            response = requests.get(f"{agent_url}/.well-known/agent.json", timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to discover {agent_name}: {e}")
        return None
    
    def send_message_to_agent(self, agent_name, message_text, context_id=None):
        """Send an A2A message to another agent"""
        agent_card = self.discover_agent(agent_name)
        if not agent_card:
            return {"error": f"Could not discover {agent_name}"}
        
        # Get the A2A endpoint
        a2a_interface = None
        for interface in agent_card.get("interfaces", []):
            if interface.get("type") == "a2a":
                a2a_interface = interface
                break
        
        if not a2a_interface:
            return {"error": f"{agent_name} doesn't support A2A protocol"}
        
        # Create A2A message
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "role": "agent",
                    "parts": [{"kind": "text", "text": message_text}],
                    "messageId": str(uuid.uuid4()),
                    "contextId": context_id
                }
            }
        }
        
        try:
            response = requests.post(
                a2a_interface["url"],
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Message sent to {agent_name}: {message_text[:50]}...")
                return result.get("result", {})
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.RequestException as e:
            self.logger.error(f"Failed to send message to {agent_name}: {e}")
            return {"error": str(e)}
    
    def create_agent_card(self):
        """Create agent discovery card"""
        return {
            "schemaVersion": "0.2.0",
            "agent": {
                "name": self.name,
                "description": f"A specialized {self.name.lower()} agent for multi-agent collaboration",
                "version": "1.0.0",
                "capabilities": self.capabilities
            },
            "capabilities": {
                "textGeneration": True,
                "imageGeneration": False,
                "fileProcessing": False,
                "realTimeInteraction": True
            },
            "interfaces": [
                {
                    "type": "a2a",
                    "url": f"{self.base_url}/a2a/v1/",
                    "methods": ["message/send", "tasks/get", "tasks/cancel"]
                }
            ],
            "authentication": {"required": False}
        }

class TravelAgent(A2AAgent):
    """Travel Agent - Coordinates trip planning"""
    
    def __init__(self):
        super().__init__("TravelAgent", 8001, [
            "trip_planning", "flight_booking", "hotel_booking", "coordination"
        ])
    
    def process_message(self, message_text, context_id=None):
        """Process travel-related requests"""
        text = message_text.lower()
        
        if "book trip" in text or "plan trip" in text:
            return self.plan_trip(message_text, context_id)
        elif "hello" in text or "hi" in text:
            return "Hello! I'm the Travel Agent. I can help you plan and book trips. Try asking me to 'book a trip to London for 3 days'."
        else:
            return f"I'm the Travel Agent. I can help with trip planning and booking. You said: '{message_text}'"
    
    def plan_trip(self, request, context_id):
        """Coordinate a multi-agent trip planning workflow"""
        self.logger.info("🛫 Starting trip planning coordination...")
        
        # Step 1: Check calendar availability
        calendar_response = self.send_message_to_agent(
            "CalendarAgent", 
            "What dates are available for a 3-day trip in the next month?",
            context_id
        )
        
        if "error" in calendar_response:
            return "Sorry, I couldn't reach the Calendar Agent to check availability."
        
        # Extract dates from calendar response
        available_dates = "April 15-17 or May 8-10"  # Simplified for demo
        
        # Step 2: Check budget with Expense Agent
        expense_response = self.send_message_to_agent(
            "ExpenseAgent",
            "What's the available budget for a London business trip? Estimated cost: $2000",
            context_id
        )
        
        # Step 3: Get weather information
        weather_response = self.send_message_to_agent(
            "WeatherAgent",
            "What's the weather forecast for London in the next month?",
            context_id
        )
        
        # Compile comprehensive trip plan
        trip_plan = f"""
🛫 TRIP PLANNING COMPLETE 🛫

📅 AVAILABILITY (from Calendar Agent):
Available dates: {available_dates}

💰 BUDGET APPROVAL (from Expense Agent):
{self.extract_response_text(expense_response)}

🌤️ WEATHER FORECAST (from Weather Agent):
{self.extract_response_text(weather_response)}

✅ RECOMMENDED TRIP:
- Destination: London
- Dates: April 15-17, 2024
- Budget: $2000 (approved)
- Flight: $800 (direct)
- Hotel: $400/night × 3 nights = $1200
- Weather: Pack business attire and light jacket

🎯 All agents have coordinated successfully! Ready to proceed with booking.
        """
        
        return trip_plan.strip()
    
    def extract_response_text(self, agent_response):
        """Extract text from agent response"""
        if "error" in agent_response:
            return f"Error: {agent_response['error']}"
        
        # Look for agent response in history
        history = agent_response.get("history", [])
        for message in reversed(history):
            if message.get("role") == "agent":
                for part in message.get("parts", []):
                    if part.get("kind") == "text":
                        return part.get("text", "No response")
        
        return "No response received"

class CalendarAgent(A2AAgent):
    """Calendar Agent - Manages schedules and availability"""
    
    def __init__(self):
        super().__init__("CalendarAgent", 8002, [
            "schedule_management", "availability_checking", "calendar_blocking"
        ])
    
    def process_message(self, message_text, context_id=None):
        """Process calendar-related requests"""
        text = message_text.lower()
        
        if "available" in text or "dates" in text or "schedule" in text:
            return self.check_availability(message_text)
        elif "block" in text or "reserve" in text:
            return self.block_calendar(message_text)
        elif "hello" in text or "hi" in text:
            return "Hello! I'm the Calendar Agent. I manage schedules and check availability for trips and meetings."
        else:
            return f"I'm the Calendar Agent. I can check availability and manage schedules. You asked: '{message_text}'"
    
    def check_availability(self, request):
        """Check calendar availability"""
        # Simulate calendar checking
        available_slots = [
            {
                "start": "2024-04-15",
                "end": "2024-04-17", 
                "conflicts": "none",
                "confidence": "high"
            },
            {
                "start": "2024-05-08",
                "end": "2024-05-10",
                "conflicts": "minor meeting (moveable)",
                "confidence": "medium"
            }
        ]
        
        response = "📅 CALENDAR AVAILABILITY REPORT:\n\n"
        for slot in available_slots:
            response += f"✅ {slot['start']} to {slot['end']}\n"
            response += f"   Conflicts: {slot['conflicts']}\n"
            response += f"   Confidence: {slot['confidence']}\n\n"
        
        response += "Recommendation: April 15-17 looks perfect with no conflicts!"
        return response
    
    def block_calendar(self, request):
        """Block calendar for confirmed trips"""
        return "✅ Calendar blocked successfully. Meeting invites sent to stakeholders."

class ExpenseAgent(A2AAgent):
    """Expense Agent - Handles budgets and cost validation"""
    
    def __init__(self):
        super().__init__("ExpenseAgent", 8003, [
            "budget_management", "expense_tracking", "policy_validation"
        ])
    
    def process_message(self, message_text, context_id=None):
        """Process expense-related requests"""
        text = message_text.lower()
        
        if "budget" in text or "cost" in text or "expense" in text:
            return self.check_budget(message_text)
        elif "approve" in text:
            return self.approve_expense(message_text)
        elif "hello" in text or "hi" in text:
            return "Hello! I'm the Expense Agent. I manage budgets, validate costs, and ensure policy compliance."
        else:
            return f"I'm the Expense Agent. I handle budget and expense management. You mentioned: '{message_text}'"
    
    def check_budget(self, request):
        """Check budget availability and policy compliance"""
        # Extract cost from request (simplified)
        estimated_cost = 2000  # Extracted from request
        
        budget_analysis = f"""
💰 BUDGET ANALYSIS REPORT:

💳 Available Budget: $5,000
📊 Estimated Cost: ${estimated_cost}
✅ Status: APPROVED ✅

📋 Policy Compliance:
  ✅ Within daily limits ($300/day)
  ✅ Business class flight approved
  ✅ 4-star hotel approved
  ✅ Expense category: Business Travel

💡 Recommendations:
  • Consider business class upgrade (+$300)
  • Remaining budget after trip: ${5000 - estimated_cost}
  • Pre-approval code: BT-2024-0415
        """
        return budget_analysis.strip()
    
    def approve_expense(self, request):
        """Approve expense requests"""
        return "✅ Expense approved! Reference number: EXP-2024-0415-001"

class WeatherAgent(A2AAgent):
    """Weather Agent - Provides weather forecasts and recommendations"""
    
    def __init__(self):
        super().__init__("WeatherAgent", 8004, [
            "weather_forecasting", "travel_recommendations", "packing_advice"
        ])
    
    def process_message(self, message_text, context_id=None):
        """Process weather-related requests"""
        text = message_text.lower()
        
        if "weather" in text or "forecast" in text:
            return self.get_weather_forecast(message_text)
        elif "pack" in text or "clothing" in text:
            return self.get_packing_advice(message_text)
        elif "hello" in text or "hi" in text:
            return "Hello! I'm the Weather Agent. I provide weather forecasts and travel packing recommendations."
        else:
            return f"I'm the Weather Agent. I can help with weather forecasts and packing advice. You asked: '{message_text}'"
    
    def get_weather_forecast(self, request):
        """Get weather forecast for destination"""
        # Simulate weather API call
        forecast = f"""
🌤️ LONDON WEATHER FORECAST:

📅 April 15-17, 2024:
  🌤️ Day 1: Partly cloudy, 16°C (61°F)
  🌧️ Day 2: Light rain, 14°C (57°F) 
  ☀️ Day 3: Sunny, 18°C (64°F)

🎒 PACKING RECOMMENDATIONS:
  ✅ Light waterproof jacket (rain expected)
  ✅ Business attire for meetings
  ✅ Comfortable walking shoes
  ✅ Umbrella (essential for Day 2)
  ✅ Layers (temperatures vary)

🌡️ Overall: Typical spring weather in London. Pack for mild temperatures and possible rain.
        """
        return forecast.strip()
    
    def get_packing_advice(self, request):
        """Provide packing recommendations"""
        return "🎒 Pack layers, waterproof jacket, business attire, and comfortable shoes for London spring weather!"

class A2AHandler(BaseHTTPRequestHandler):
    """HTTP handler for A2A protocol requests"""
    
    def __init__(self, *args, agent=None, **kwargs):
        self.agent = agent
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests - agent discovery"""
        if self.path == "/.well-known/agent.json":
            agent_card = self.agent.create_agent_card()
            self.send_json_response(agent_card)
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests - A2A messages"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            if method == "message/send":
                response = self.handle_message_send(params, request_id)
                self.send_json_response(response)
            else:
                self.send_error_response(f"Method not found: {method}", -32601, request_id)
                
        except Exception as e:
            self.agent.logger.error(f"Error processing request: {e}")
            self.send_error_response("Internal error", -32603)
    
    def handle_message_send(self, params, request_id):
        """Handle message/send method"""
        message = params.get("message", {})
        parts = message.get("parts", [])
        
        # Extract text content
        text_content = ""
        for part in parts:
            if part.get("kind") == "text":
                text_content += part.get("text", "")
        
        context_id = message.get("contextId")
        
        # Process the message
        ai_response = self.agent.process_message(text_content, context_id)
        
        # Create task response
        task_id = str(uuid.uuid4())
        if not context_id:
            context_id = str(uuid.uuid4())
        
        # Create message objects for history
        user_message = {
            "role": message.get("role", "user"),
            "parts": parts,
            "messageId": message.get("messageId", str(uuid.uuid4())),
            "taskId": task_id,
            "contextId": context_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        agent_message = {
            "role": "agent",
            "parts": [{"kind": "text", "text": ai_response}],
            "messageId": str(uuid.uuid4()),
            "taskId": task_id,
            "contextId": context_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        task = {
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": "completed",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "history": [user_message, agent_message],
            "artifacts": [],
            "kind": "task",
            "metadata": {}
        }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": task
        }
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error_response(self, message, code, request_id=None):
        """Send JSON-RPC error response"""
        error_response = {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message}
        }
        if request_id is not None:
            error_response["id"] = request_id
        
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(error_response).encode())

def create_handler(agent):
    """Create handler with agent instance"""
    def handler(*args, **kwargs):
        return A2AHandler(*args, agent=agent, **kwargs)
    return handler

def start_agent(agent_class):
    """Start an individual agent server"""
    agent = agent_class()
    handler = create_handler(agent)
    server = HTTPServer(('localhost', agent.port), handler)
    
    agent.logger.info(f"🚀 {agent.name} starting on {agent.base_url}")
    agent.logger.info(f"📋 Agent Card: {agent.base_url}/.well-known/agent.json")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        agent.logger.info(f"🛑 {agent.name} stopping...")
        server.shutdown()

def start_multi_agent_demo():
    """Start all agents and run a demo workflow"""
    print("🤖 Multi-Agent A2A System Starting...")
    print("=" * 50)
    
    # List of agent classes
    agent_classes = [TravelAgent, CalendarAgent, ExpenseAgent, WeatherAgent]
    
    # Start each agent in a separate thread
    threads = []
    for agent_class in agent_classes:
        thread = threading.Thread(target=start_agent, args=(agent_class,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  # Stagger startup
    
    # Give agents time to start
    print("⏳ Waiting for all agents to start...")
    time.sleep(3)
    
    # Demo the multi-agent workflow
    print("\n🎭 Running Multi-Agent Trip Planning Demo...")
    print("=" * 50)
    
    # Create a travel agent client to trigger the workflow
    travel_agent = TravelAgent()
    
    # Simulate user request
    print("👤 User Request: 'Book a trip to London for 3 days'")
    print("\n🔄 Agents collaborating...")
    
    result = travel_agent.process_message("book trip to London for 3 days", str(uuid.uuid4()))
    
    print("\n📋 FINAL RESULT:")
    print("=" * 50)
    print(result)
    
    print("\n✅ Multi-agent collaboration complete!")
    print("💡 All 4 agents worked together without a supervisor!")
    print("\nPress Ctrl+C to stop all agents...")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all agents...")

if __name__ == "__main__":
    start_multi_agent_demo() 