#!/usr/bin/env python3
"""
A2A Protocol Agent Server Implementation
A simple AI agent that follows the A2A protocol for agent-to-agent communication.
"""

import json
import uuid
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskManager:
    """Manages tasks and their states"""
    def __init__(self):
        self.tasks = {}
        self.contexts = {}
    
    def create_task(self, message, context_id=None):
        task_id = str(uuid.uuid4())
        if not context_id:
            context_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": "submitted",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "history": [message],
            "artifacts": [],
            "kind": "task",
            "metadata": {}
        }
        
        self.tasks[task_id] = task
        if context_id not in self.contexts:
            self.contexts[context_id] = []
        self.contexts[context_id].append(task_id)
        
        return task
    
    def update_task_status(self, task_id, state, message=None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = {
                "state": state,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            if message:
                self.tasks[task_id]["status"]["message"] = message
                self.tasks[task_id]["history"].append(message)
    
    def add_artifact(self, task_id, artifact):
        if task_id in self.tasks:
            self.tasks[task_id]["artifacts"].append(artifact)
    
    def get_task(self, task_id):
        return self.tasks.get(task_id)

class SimpleAIAgent:
    """A simple AI agent that can process different types of requests"""
    
    def __init__(self):
        self.task_manager = TaskManager()
        self.agent_info = {
            "name": "SimpleA2AAgent",
            "description": "A demonstration A2A protocol agent",
            "version": "1.0.0",
            "capabilities": [
                "text_processing",
                "task_management",
                "simple_calculations"
            ]
        }
    
    def process_message(self, message_content):
        """Process a text message and return a response"""
        text = message_content.lower()
        
        if "hello" in text or "hi" in text:
            return "Hello! I'm a simple A2A agent. I can help with basic tasks, calculations, or just chat!"
        
        elif "calculate" in text or "math" in text:
            # Simple math processing
            if "2+2" in text or "2 + 2" in text:
                return "2 + 2 = 4"
            elif "10*5" in text or "10 * 5" in text:
                return "10 * 5 = 50"
            else:
                return "I can do simple math! Try asking me '2+2' or '10*5'"
        
        elif "time" in text:
            return f"Current time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        elif "joke" in text:
            return "Why did the AI cross the road? To get to the other protocol! 🤖"
        
        elif "help" in text:
            return """I can help with:
            - Greetings (say hello!)
            - Simple math (ask me to calculate 2+2)
            - Current time
            - Tell jokes
            - General conversation"""
        
        else:
            return f"I received your message: '{message_content}'. I'm a simple demo agent, so my responses are limited. Try asking for help!"

class A2AProtocolHandler(BaseHTTPRequestHandler):
    """HTTP handler for A2A protocol requests"""
    
    def __init__(self, *args, agent=None, **kwargs):
        self.agent = agent
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests - mainly for agent discovery"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == "/.well-known/agent.json":
            # Agent Card - agent discovery endpoint
            agent_card = {
                "schemaVersion": "0.2.0",
                "agent": self.agent.agent_info,
                "capabilities": {
                    "textGeneration": True,
                    "imageGeneration": False,
                    "fileProcessing": False,
                    "realTimeInteraction": False
                },
                "interfaces": [
                    {
                        "type": "a2a",
                        "url": "http://localhost:8000/a2a/v1/",
                        "methods": ["message/send", "tasks/get", "tasks/cancel"]
                    }
                ],
                "authentication": {
                    "required": False
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(agent_card, indent=2).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests - A2A protocol messages"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Validate JSON-RPC format
            if request_data.get("jsonrpc") != "2.0":
                self.send_error_response("Invalid JSON-RPC version", -32600)
                return
            
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            logger.info(f"Received method: {method}")
            
            if method == "message/send":
                response = self.handle_message_send(params, request_id)
            elif method == "tasks/get":
                response = self.handle_tasks_get(params, request_id)
            elif method == "tasks/cancel":
                response = self.handle_tasks_cancel(params, request_id)
            else:
                self.send_error_response(f"Method not found: {method}", -32601, request_id)
                return
            
            self.send_json_response(response)
            
        except json.JSONDecodeError:
            self.send_error_response("Parse error", -32700)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_error_response("Internal error", -32603, request_data.get("id"))
    
    def handle_message_send(self, params, request_id):
        """Handle message/send method"""
        message = params.get("message", {})
        
        # Extract message content
        parts = message.get("parts", [])
        text_content = ""
        for part in parts:
            if part.get("kind") == "text":
                text_content += part.get("text", "")
        
        # Create message object for history
        message_obj = {
            "role": message.get("role", "user"),
            "parts": parts,
            "messageId": message.get("messageId", str(uuid.uuid4())),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Check if this is continuing an existing task
        context_id = message.get("contextId")
        task_id = message.get("taskId")
        
        if task_id and task_id in self.agent.task_manager.tasks:
            # Continue existing task
            task = self.agent.task_manager.get_task(task_id)
            task["history"].append(message_obj)
        else:
            # Create new task
            task = self.agent.task_manager.create_task(message_obj, context_id)
            task_id = task["id"]
        
        # Process the message
        self.agent.task_manager.update_task_status(task_id, "working")
        
        # Simulate some processing time
        time.sleep(0.5)
        
        # Get AI response
        ai_response = self.agent.process_message(text_content)
        
        # Create response message
        response_message = {
            "role": "agent",
            "parts": [
                {
                    "kind": "text",
                    "text": ai_response
                }
            ],
            "messageId": str(uuid.uuid4()),
            "taskId": task_id,
            "contextId": task["contextId"],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Update task
        self.agent.task_manager.update_task_status(task_id, "completed", response_message)
        
        # Return completed task
        task = self.agent.task_manager.get_task(task_id)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": task
        }
    
    def handle_tasks_get(self, params, request_id):
        """Handle tasks/get method"""
        task_id = params.get("id")
        task = self.agent.task_manager.get_task(task_id)
        
        if not task:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Task not found"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": task
        }
    
    def handle_tasks_cancel(self, params, request_id):
        """Handle tasks/cancel method"""
        task_id = params.get("id")
        task = self.agent.task_manager.get_task(task_id)
        
        if not task:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Task not found"
                }
            }
        
        self.agent.task_manager.update_task_status(task_id, "cancelled")
        task = self.agent.task_manager.get_task(task_id)
        
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
            "error": {
                "code": code,
                "message": message
            }
        }
        if request_id is not None:
            error_response["id"] = request_id
        
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def create_handler(agent):
    """Create handler with agent instance"""
    def handler(*args, **kwargs):
        return A2AProtocolHandler(*args, agent=agent, **kwargs)
    return handler

def run_server():
    """Run the A2A agent server"""
    agent = SimpleAIAgent()
    handler = create_handler(agent)
    
    server = HTTPServer(('localhost', 8000), handler)
    
    logger.info("A2A Agent Server starting on http://localhost:8000")
    logger.info("Agent Card available at: http://localhost:8000/.well-known/agent.json")
    logger.info("A2A endpoint: http://localhost:8000/a2a/v1/")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopping...")
        server.shutdown()

if __name__ == "__main__":
    run_server() 