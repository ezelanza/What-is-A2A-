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
import signal
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Global variables to track running servers
running_servers = []
shutdown_event = threading.Event()

# LLM Configuration
LLM_CONFIG = {
    "provider": "ollama",  # Options: "ollama", "openai", "anthropic"
    "model": "llama3.2:3b",  # Local model for privacy and no API costs
    "base_url": "http://localhost:11434",  # Ollama default URL
    "api_key": None  # Not needed for Ollama
}

class LLMInterface:
    """Universal LLM interface supporting multiple providers"""
    
    def __init__(self, config=None):
        self.config = config or LLM_CONFIG
        
    def query_llm(self, prompt, system_prompt=None):
        """Query the configured LLM with a prompt"""
        try:
            if self.config["provider"] == "ollama":
                return self._query_ollama(prompt, system_prompt)
            elif self.config["provider"] == "openai":
                return self._query_openai(prompt, system_prompt)
            elif self.config["provider"] == "anthropic":
                return self._query_anthropic(prompt, system_prompt)
            else:
                return f"Error: Unsupported LLM provider: {self.config['provider']}"
        except Exception as e:
            return f"LLM Error: {str(e)} - Falling back to basic analysis"
    
    def _query_ollama(self, prompt, system_prompt=None):
        """Query Ollama local LLM"""
        url = f"{self.config['base_url']}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
        payload = {
            "model": self.config["model"],
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            raise Exception(f"Ollama HTTP {response.status_code}")
    
    def _query_openai(self, prompt, system_prompt=None):
        """Query OpenAI API (requires openai package)"""
        try:
            import openai
            openai.api_key = self.config["api_key"]
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model=self.config["model"],
                messages=messages
            )
            return response.choices[0].message.content
        except ImportError:
            raise Exception("OpenAI package not installed. Install with: pip install openai")
    
    def _query_anthropic(self, prompt, system_prompt=None):
        """Query Anthropic Claude API (requires anthropic package)"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.config["api_key"])
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}"
            
            response = client.completions.create(
                model=self.config["model"],
                prompt=full_prompt,
                max_tokens_to_sample=1000
            )
            return response.completion
        except ImportError:
            raise Exception("Anthropic package not installed. Install with: pip install anthropic")

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

# Global instances
registry = AgentRegistry()
llm = LLMInterface()

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
TRIP PLANNING COMPLETE

AVAILABILITY (from Calendar Agent):
Available dates: {available_dates}

BUDGET APPROVAL (from Expense Agent):
{self.extract_response_text(expense_response)}

WEATHER FORECAST (from Weather Agent):
{self.extract_response_text(weather_response)}

RECOMMENDED TRIP:
- Destination: London
- Dates: April 15-17, 2024
- Budget: $2000 (approved)
- Flight: $800 (direct)
- Hotel: $400/night × 3 nights = $1200
- Weather: Pack business attire and light jacket

All agents have coordinated successfully! Ready to proceed with booking.
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
        
        response = "CALENDAR AVAILABILITY REPORT:\n\n"
        for slot in available_slots:
            response += f"AVAILABLE: {slot['start']} to {slot['end']}\n"
            response += f"   Conflicts: {slot['conflicts']}\n"
            response += f"   Confidence: {slot['confidence']}\n\n"
        
        response += "Recommendation: April 15-17 looks perfect with no conflicts!"
        return response
    
    def block_calendar(self, request):
        """Block calendar for confirmed trips"""
        return "Calendar blocked successfully. Meeting invites sent to stakeholders."

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
BUDGET ANALYSIS REPORT:

Available Budget: $5,000
Estimated Cost: ${estimated_cost}
Status: APPROVED

Policy Compliance:
  • Within daily limits ($300/day)
  • Business class flight approved
  • 4-star hotel approved
  • Expense category: Business Travel

Recommendations:
  • Consider business class upgrade (+$300)
  • Remaining budget after trip: ${5000 - estimated_cost}
  • Pre-approval code: BT-2024-0415
        """
        return budget_analysis.strip()
    
    def approve_expense(self, request):
        """Approve expense requests"""
        return "Expense approved! Reference number: EXP-2024-0415-001"

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
LONDON WEATHER FORECAST:

April 15-17, 2024:
  Day 1: Partly cloudy, 16°C (61°F)
  Day 2: Light rain, 14°C (57°F) 
  Day 3: Sunny, 18°C (64°F)

PACKING RECOMMENDATIONS:
  • Light waterproof jacket (rain expected)
  • Business attire for meetings
  • Comfortable walking shoes
  • Umbrella (essential for Day 2)
  • Layers (temperatures vary)

Overall: Typical spring weather in London. Pack for mild temperatures and possible rain.
        """
        return forecast.strip()
    
    def get_packing_advice(self, request):
        """Provide packing recommendations"""
        return "Pack layers, waterproof jacket, business attire, and comfortable shoes for London spring weather!"

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
    
    # Track the server for shutdown
    running_servers.append(server)
    
    agent.logger.info(f"{agent.name} starting on {agent.base_url}")
    agent.logger.info(f"Agent Card: {agent.base_url}/.well-known/agent.json")
    
    def serve_with_shutdown():
        while not shutdown_event.is_set():
            server.timeout = 1
            server.handle_request()
        agent.logger.info(f"{agent.name} stopping...")
        server.server_close()
    
    serve_with_shutdown()

class InterfaceAgent(A2AAgent):
    """Smart Interface Agent - Natural language entry point that coordinates with other agents via A2A"""
    
    def __init__(self):
        super().__init__("InterfaceAgent", 8000, [
            "natural_language_processing", "agent_coordination", "user_interface"
        ])
        
    def process_message(self, message_text, context_id=None):
        """Process user input and intelligently coordinate with appropriate agents"""
        # Analyze user intent from natural language
        intent_analysis = self.analyze_user_intent(message_text)
        
        if intent_analysis["requires_coordination"]:
            return self.coordinate_multi_agent_response(message_text, intent_analysis, context_id)
        else:
            return self.handle_single_agent_request(message_text, intent_analysis, context_id)
    
    def analyze_user_intent(self, message_text):
        """Use LLM to intelligently analyze user intent and determine agent coordination needs"""
        
        system_prompt = """You are an intelligent A2A (Agent-to-Agent) routing system. Analyze user requests and determine which specialized agents should handle them.

Available Agents:
- TravelAgent: Trip planning, booking flights/hotels, travel coordination
- CalendarAgent: Schedule management, availability checking, appointment booking
- ExpenseAgent: Budget analysis, expense tracking, financial approval
- WeatherAgent: Weather forecasts, packing advice, climate information

Your task is to analyze the user's request and respond with ONLY a JSON object (no other text) in this exact format:

{
    "type": "query_type",
    "requires_coordination": true/false,
    "agents_needed": ["Agent1", "Agent2"],
    "primary_agent": "PrimaryAgent",
    "reasoning": "Brief explanation of decision"
}

Rules:
- If the request involves complex trip planning, vacation planning, or business travel, set requires_coordination=true and include all relevant agents
- For simple single-topic queries, set requires_coordination=false and use only the relevant agent
- Always include TravelAgent as primary for trip planning
- For ambiguous requests, default to TravelAgent but set requires_coordination=false"""

        prompt = f"Analyze this user request: '{message_text}'"
        
        try:
            llm_response = llm.query_llm(prompt, system_prompt)
            
            # Extract JSON from response (in case LLM adds extra text)
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                intent_analysis = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["type", "requires_coordination", "agents_needed", "primary_agent"]
                if all(field in intent_analysis for field in required_fields):
                    self.logger.info(f"LLM Intent Analysis: {intent_analysis['reasoning']}")
                    return intent_analysis
                    
        except Exception as e:
            self.logger.warning(f"LLM analysis failed: {e} - Using fallback analysis")
        
        # Fallback to basic analysis if LLM fails
        return self._fallback_intent_analysis(message_text)
    
    def _fallback_intent_analysis(self, message_text):
        """Simple fallback analysis if LLM is not available"""
        text = message_text.lower()
        
        # Simple detection for complex requests
        complex_indicators = ["plan", "organize", "book a trip", "vacation", "business trip", "coordinate"]
        is_complex = any(indicator in text for indicator in complex_indicators)
        
        if is_complex:
            return {
                "type": "trip_planning",
                "requires_coordination": True,
                "agents_needed": ["TravelAgent", "CalendarAgent", "ExpenseAgent", "WeatherAgent"],
                "primary_agent": "TravelAgent",
                "reasoning": "Fallback: Detected complex travel request"
            }
        
        # Single agent routing
        if any(word in text for word in ["calendar", "schedule", "available", "free", "busy"]):
            return {
                "type": "calendar_query",
                "requires_coordination": False,
                "agents_needed": ["CalendarAgent"],
                "primary_agent": "CalendarAgent",
                "reasoning": "Fallback: Calendar-related query"
            }
        elif any(word in text for word in ["budget", "cost", "expense", "money", "price"]):
            return {
                "type": "expense_query",
                "requires_coordination": False,
                "agents_needed": ["ExpenseAgent"],
                "primary_agent": "ExpenseAgent",
                "reasoning": "Fallback: Financial query"
            }
        elif any(word in text for word in ["weather", "forecast", "temperature", "rain", "sunny"]):
            return {
                "type": "weather_query",
                "requires_coordination": False,
                "agents_needed": ["WeatherAgent"],
                "primary_agent": "WeatherAgent",
                "reasoning": "Fallback: Weather query"
            }
        else:
            return {
                "type": "general_query",
                "requires_coordination": False,
                "agents_needed": ["TravelAgent"],
                "primary_agent": "TravelAgent",
                "reasoning": "Fallback: Default to travel agent"
            }
    
    def coordinate_multi_agent_response(self, message_text, intent_analysis, context_id):
        """Coordinate with multiple agents for complex requests"""
        print(f"[InterfaceAgent] Detected {intent_analysis['type']} - coordinating with multiple agents...")
        
        # Send to primary agent (usually TravelAgent for trip planning)
        primary_agent = intent_analysis["primary_agent"]
        enhanced_message = f"User request: {message_text}\n\nThis is a complex request requiring coordination with other agents. Please coordinate with CalendarAgent, ExpenseAgent, and WeatherAgent as needed."
        
        response = self.send_message_to_agent(primary_agent, enhanced_message, context_id)
        
        return f"MULTI-AGENT COORDINATION INITIATED\n\nYour request has been routed to {primary_agent} who will coordinate with other specialized agents to provide a comprehensive response.\n\n{self.extract_response_text(response)}"
    
    def handle_single_agent_request(self, message_text, intent_analysis, context_id):
        """Handle requests that can be satisfied by a single agent"""
        target_agent = intent_analysis["primary_agent"]
        print(f"[InterfaceAgent] Routing to {target_agent} for {intent_analysis['type']}")
        
        response = self.send_message_to_agent(target_agent, message_text, context_id)
        return self.extract_response_text(response)
    
    def extract_response_text(self, agent_response):
        """Extract text from agent response"""
        if isinstance(agent_response, str):
            return agent_response
            
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

class InteractiveClient:
    """Interactive client for multi-agent system"""
    
    def __init__(self):
        self.current_context_id = str(uuid.uuid4())
        self.conversation_history = []
        self.shutdown_requested = False
        
    def send_message_to_interface_agent(self, message_text):
        """Send message to the Interface Agent which will handle routing"""
        url = "http://localhost:8000/a2a/v1/"
        
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message_text}],
                    "messageId": str(uuid.uuid4()),
                    "contextId": self.current_context_id
                }
            }
        }
        
        try:
            response = requests.post(url, json=request_data, timeout=15)
            if response.status_code == 200:
                result = response.json().get("result", {})
                
                # Extract agent response
                history = result.get("history", [])
                for message in reversed(history):
                    if message.get("role") == "agent":
                        for part in message.get("parts", []):
                            if part.get("kind") == "text":
                                return part.get("text", "No response")
                
                return "No response received"
            else:
                return f"ERROR: HTTP {response.status_code}"
                
        except requests.RequestException as e:
            return f"ERROR: Connection error: {e}"
    
    def show_agent_menu(self):
        """Show available agents and natural language capabilities"""
        print("\nIntelligent A2A System - Natural Language Interface")
        print("Just speak naturally! The system will automatically coordinate with the right agents.")
        print("\nAgent Capabilities:")
        print("• InterfaceAgent - Smart routing and coordination (port 8000)")
        print("• TravelAgent    - Trip planning and coordination (port 8001)")
        print("• CalendarAgent  - Schedule management (port 8002)")
        print("• ExpenseAgent   - Budget and expense tracking (port 8003)")
        print("• WeatherAgent   - Weather forecasts (port 8004)")
        print("\nCommands: 'help', 'agents', 'history', 'clear', 'quit'")
    
    def show_help(self):
        """Show help information"""
        help_text = """
HELP - Intelligent A2A System with Natural Language

NATURAL LANGUAGE INTERFACE:
  Just speak naturally! No keywords needed. The Interface Agent will analyze
  your intent and automatically coordinate with the appropriate specialist agents.

TRIP PLANNING EXAMPLES:
  • "I want to plan a business trip to London for 3 days"
  • "Can you help me organize a vacation to Paris?"
  • "I need to book travel to Tokyo next month"
  • "Plan a weekend getaway somewhere warm"

SPECIFIC QUERIES:
  • "When am I free next month?" (→ Calendar Agent)
  • "What's my travel budget?" (→ Expense Agent)  
  • "What's the weather like in London?" (→ Weather Agent)
  • "Find me a flight to New York" (→ Travel Agent)

HOW IT WORKS:
  1. You speak naturally to the Interface Agent (no keywords!)
  2. It analyzes your intent using natural language processing
  3. It automatically discovers and coordinates with relevant agents
  4. Agents collaborate peer-to-peer using A2A protocol
  5. You get a comprehensive response

WATCH THE MAGIC:
  Complex requests trigger multi-agent coordination:
  [Interface→Travel] "User wants trip to London..."
  [Travel→Calendar] "Check availability..."
  [Calendar→Travel] "April 15-17 is free!"
  [Travel→Expense] "Budget check for $2000..."
  [Expense→Travel] "Approved!"
  [Travel→Weather] "Weather forecast needed..."

COMMANDS:
  'help'    - Show this help
  'agents'  - List available agents  
  'history' - Show conversation history
  'clear'   - Clear history
  'quit'    - Exit system and stop all agents

EXAMPLES TO TRY:
  • "I need help planning a trip to Italy"
  • "Check if I'm available for travel next week"
  • "How much can I spend on vacation?"
  • "Should I pack warm clothes for London in March?"
        """
        print(help_text)
    
    def interactive_chat(self):
        """Start interactive chat with intelligent multi-agent system"""
        print("Welcome to the Intelligent A2A System!")
        print("Just speak naturally - no keywords needed. The system will automatically")
        print("coordinate with the right agents based on your request.")
        print("Type 'help' for examples and detailed instructions.")
        
        self.show_agent_menu()
        
        while True:
            try:
                print("\n" + "─" * 50)
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye! Shutting down all agents...")
                    self.shutdown_requested = True
                    shutdown_event.set()
                    # Give a moment for shutdown to process
                    time.sleep(1)
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                elif user_input.lower() == 'agents':
                    self.show_agent_menu()
                    continue
                
                elif user_input.lower() == 'history':
                    if self.conversation_history:
                        print("\nConversation History:")
                        for i, entry in enumerate(self.conversation_history, 1):
                            print(f"{i}. You: {entry['input']}")
                            print(f"   System: {entry['response'][:100]}...")
                    else:
                        print("No conversation history yet.")
                    continue
                
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    self.current_context_id = str(uuid.uuid4())
                    print("History cleared and new context started.")
                    continue
                
                # Send natural language input to Interface Agent
                print("Processing your request...")
                print("The Interface Agent will analyze your intent and coordinate with appropriate agents...")
                
                # Send message to Interface Agent for intelligent routing
                response = self.send_message_to_interface_agent(user_input)
                
                print(f"\nSystem Response:")
                print("─" * 30)
                print(response)
                
                # Store in history
                self.conversation_history.append({
                    'input': user_input,
                    'response': response
                })
                
                # Show tip for multi-agent coordination
                if "MULTI-AGENT COORDINATION" in response:
                    print("\nNOTE: You just triggered multi-agent coordination!")
                    print("   The Interface Agent detected a complex request and coordinated")
                    print("   with multiple specialist agents using pure A2A protocol.")
                
            except KeyboardInterrupt:
                print("\nGoodbye! Shutting down agents...")
                shutdown_event.set()
                break
            except EOFError:
                print("\nGoodbye! Shutting down agents...")
                shutdown_event.set()
                break

def shutdown_all_agents():
    """Properly shutdown all running servers"""
    print("Stopping all agent servers...")
    shutdown_event.set()
    
    # Close all tracked servers
    for server in running_servers:
        try:
            server.server_close()
        except:
            pass
    
    running_servers.clear()
    print("All agents stopped.")

def start_multi_agent_system():
    """Start all agents and interactive interface"""
    print("Intelligent Multi-Agent A2A System Starting...")
    print("=" * 50)
    
    # List of agent classes - Interface Agent first, then specialists
    agent_classes = [InterfaceAgent, TravelAgent, CalendarAgent, ExpenseAgent, WeatherAgent]
    
    # Start each agent in a separate thread
    threads = []
    for agent_class in agent_classes:
        thread = threading.Thread(target=start_agent, args=(agent_class,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  # Stagger startup
    
    # Give agents time to start
    print("Waiting for all agents to start...")
    time.sleep(4)  # Extra time for 5 agents
    
    print("All agents are running!")
    print("Intelligent A2A System ready with natural language processing:")
    print("   Interface Agent: http://localhost:8000 (Smart routing & coordination)")
    print("   Travel Agent:    http://localhost:8001 (Trip planning)")
    print("   Calendar Agent:  http://localhost:8002 (Schedule management)") 
    print("   Expense Agent:   http://localhost:8003 (Budget tracking)")
    print("   Weather Agent:   http://localhost:8004 (Weather forecasts)")
    
    # Start interactive interface
    try:
        client = InteractiveClient()
        client.interactive_chat()
    except KeyboardInterrupt:
        print("\nShutting down all agents...")
    finally:
        shutdown_all_agents()

def start_demo_mode():
    """Run the intelligent A2A demo"""
    print("Running Intelligent A2A Demo...")
    print("=" * 50)
    
    # List of agent classes including Interface Agent
    agent_classes = [InterfaceAgent, TravelAgent, CalendarAgent, ExpenseAgent, WeatherAgent]
    
    # Start each agent in a separate thread
    threads = []
    for agent_class in agent_classes:
        thread = threading.Thread(target=start_agent, args=(agent_class,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  # Stagger startup
    
    # Give agents time to start
    print("Waiting for all agents to start...")
    time.sleep(4)
    
    # Create an interface agent client to trigger the workflow
    interface_agent = InterfaceAgent()
    
    # Simulate user request using natural language
    print("User Request: 'I want to plan a business trip to London for 3 days'")
    print("\nInterface Agent analyzing intent and coordinating with specialists...")
    
    result = interface_agent.process_message("I want to plan a business trip to London for 3 days", str(uuid.uuid4()))
    
    print("\nFINAL RESULT:")
    print("=" * 50)
    print(result)
    
    print("\nIntelligent multi-agent collaboration complete!")
    print("The Interface Agent used natural language processing to coordinate")
    print("with 4 specialist agents without any central supervisor!")
    print("\nPress Ctrl+C to stop all agents...")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all agents...")
    finally:
        shutdown_all_agents()

def main():
    """Main function - choose interactive or demo mode"""
    print("Intelligent Multi-Agent A2A Protocol System")
    print("=" * 45)
    print("Revolutionary peer-to-peer agent coordination with natural language!")
    print("\nChoose mode:")
    print("1. Interactive Mode (Recommended) - Natural language chat")
    print("2. Demo Mode - Automated intelligent coordination demo")
    
    while True:
        try:
            choice = input("\nEnter choice (1-2): ").strip()
            
            if choice == "1":
                start_multi_agent_system()
                break
            elif choice == "2":
                start_demo_mode()
                break
            else:
                print("Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            shutdown_all_agents()
            break
        except EOFError:
            print("\nGoodbye!")
            shutdown_all_agents()
            break

if __name__ == "__main__":
    main() 