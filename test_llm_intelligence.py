#!/usr/bin/env python3
"""
Test script demonstrating LLM-based intelligent A2A agent routing

This script shows how the system now uses real LLM intelligence instead of 
hardcoded keyword matching to understand user intent and route requests.
"""

import json
import requests
from multi_agent_travel import LLMInterface, LLM_CONFIG

def test_llm_routing():
    """Test LLM-based intent analysis"""
    
    print("🧠 TESTING LLM-BASED INTELLIGENT ROUTING")
    print("="*60)
    
    # Initialize LLM interface
    llm = LLMInterface()
    
    # Test various user requests
    test_requests = [
        "I want to plan a business trip to Tokyo next month for a conference",
        "What's the weather like in Paris this weekend?",
        "Can you check if I'm available on Thursday afternoon?",
        "I need to know my travel budget for this quarter",
        "Plan a romantic getaway to Italy for my anniversary",
        "Help me organize a family vacation to Hawaii with 4 people",
        "Is it going to rain tomorrow? I need to pack appropriately",
        "What meetings do I have scheduled for next week?",
        "How much did I spend on travel last month?",
        "Book me a flight to London and find a nice hotel near the city center",
        "I'm thinking about visiting somewhere warm in December",
        "Can we coordinate a team retreat that includes travel and accommodation?",
        "What's my expense approval limit for international travel?",
        "I need to reschedule my Paris trip due to bad weather forecasts"
    ]
    
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

    print(f"LLM Configuration: {LLM_CONFIG['provider']} - {LLM_CONFIG['model']}")
    print("\nTesting various user requests...\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"{i:2d}. USER: {request}")
        
        prompt = f"Analyze this user request: '{request}'"
        
        try:
            llm_response = llm.query_llm(prompt, system_prompt)
            
            # Extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                intent_analysis = json.loads(json_str)
                
                print(f"    🎯 INTENT: {intent_analysis['type']}")
                print(f"    🤝 COORDINATION: {'Yes' if intent_analysis['requires_coordination'] else 'No'}")
                print(f"    🎭 AGENTS: {', '.join(intent_analysis['agents_needed'])}")
                print(f"    ⭐ PRIMARY: {intent_analysis['primary_agent']}")
                print(f"    💭 REASONING: {intent_analysis['reasoning']}")
                
            else:
                print(f"    ❌ Invalid JSON response: {llm_response[:100]}")
                
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
        
        print()

def test_llm_availability():
    """Test if LLM is available and working"""
    print("\n🔍 TESTING LLM AVAILABILITY")
    print("="*60)
    
    llm = LLMInterface()
    
    # Simple test query
    test_prompt = "Hello, are you working correctly? Please respond with 'Yes, I am working' if you can understand this."
    
    try:
        response = llm.query_llm(test_prompt)
        print(f"✅ LLM RESPONSE: {response}")
        
        if "working" in response.lower():
            print("✅ LLM is functioning correctly!")
            return True
        else:
            print("⚠️  LLM responded but may not be functioning optimally")
            return False
            
    except Exception as e:
        print(f"❌ LLM ERROR: {e}")
        print("\n💡 TROUBLESHOOTING:")
        
        if LLM_CONFIG["provider"] == "ollama":
            print("   • Make sure Ollama is installed: https://ollama.ai/")
            print("   • Run: ollama serve")
            print(f"   • Pull the model: ollama pull {LLM_CONFIG['model']}")
            print(f"   • Test: curl {LLM_CONFIG['base_url']}/api/generate -d '{{\"model\":\"{LLM_CONFIG['model']}\",\"prompt\":\"hello\",\"stream\":false}}'")
        elif LLM_CONFIG["provider"] == "openai":
            print("   • Install: pip install openai")
            print("   • Set API key in LLM_CONFIG")
        elif LLM_CONFIG["provider"] == "anthropic":
            print("   • Install: pip install anthropic")
            print("   • Set API key in LLM_CONFIG")
            
        return False

def compare_old_vs_new():
    """Compare old keyword-based routing vs new LLM-based routing"""
    print("\n🔄 OLD vs NEW ROUTING COMPARISON")
    print("="*60)
    
    print("OLD SYSTEM (Keyword-based):")
    print("❌ Required specific keywords like 'plan trip', 'check calendar'")
    print("❌ Hardcoded rules and patterns")
    print("❌ Limited understanding of natural language")
    print("❌ Couldn't handle complex or ambiguous requests")
    print("❌ Essentially created a hidden supervisor through keyword routing")
    
    print("\nNEW SYSTEM (LLM-based):")
    print("✅ Understands natural language without keywords")
    print("✅ Intelligent context analysis")
    print("✅ Dynamic agent coordination decisions")
    print("✅ Handles complex and ambiguous requests")
    print("✅ True A2A spirit - no hardcoded supervision")
    print("✅ Fallback system ensures reliability")
    
    example_requests = [
        ("I'm thinking about a vacation", "OLD: No keywords → Default", "NEW: LLM understands vacation intent"),
        ("My boss wants me to travel", "OLD: No 'plan trip' → Confused", "NEW: LLM infers business travel context"),
        ("It's raining, should I pack?", "OLD: Weather keyword → Single agent", "NEW: LLM connects weather + packing + travel")
    ]
    
    print("\nEXAMPLE COMPARISONS:")
    for request, old_behavior, new_behavior in example_requests:
        print(f"\n📝 '{request}'")
        print(f"   {old_behavior}")
        print(f"   {new_behavior}")

def main():
    """Main test function"""
    print("🧠 A2A INTELLIGENT ROUTING TEST SUITE")
    print("=====================================")
    
    # Test LLM availability first
    if test_llm_availability():
        test_llm_routing()
    else:
        print("\n⚠️  LLM not available - system will use fallback analysis")
        print("The system will still work but with reduced intelligence.")
    
    compare_old_vs_new()
    
    print("\n🎉 BENEFITS OF LLM-BASED ROUTING:")
    print("• No hardcoded keywords or supervision")
    print("• True natural language understanding")
    print("• Dynamic, context-aware agent coordination")
    print("• Maintains pure A2A peer-to-peer spirit")
    print("• Fallback ensures reliability without LLM")

if __name__ == "__main__":
    main() 