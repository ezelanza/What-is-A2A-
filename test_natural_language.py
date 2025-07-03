#!/usr/bin/env python3
"""
Test script to demonstrate the natural language capabilities
of the Intelligent A2A Interface Agent
"""

import sys
sys.path.append('.')

from multi_agent_travel import InterfaceAgent

def test_natural_language_analysis():
    """Test the natural language analysis capabilities"""
    
    print("🤖 Testing Interface Agent Natural Language Analysis")
    print("=" * 60)
    
    # Create interface agent
    agent = InterfaceAgent()
    
    # Test cases
    test_cases = [
        "I want to plan a trip to Paris",
        "Check if I'm available next week", 
        "What's my travel budget?",
        "What's the weather like in London?",
        "I need help organizing a business trip to Tokyo for 3 days",
        "When am I free next month?",
        "Can I afford a $2000 vacation?",
        "Should I pack warm clothes for London in March?",
        "Book me a flight to New York",
        "Plan a weekend getaway somewhere warm"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. User says: '{test_input}'")
        
        # Analyze intent
        analysis = agent.analyze_user_intent(test_input)
        
        print(f"   Intent type: {analysis['type']}")
        print(f"   Coordination: {'Multi-agent' if analysis['requires_coordination'] else 'Single agent'}")
        print(f"   Primary agent: {analysis['primary_agent']}")
        if analysis['requires_coordination']:
            print(f"   Agents needed: {', '.join(analysis['agents_needed'])}")

def show_comparison():
    """Show the difference between old keyword system and new natural language"""
    
    print("\n\n📊 COMPARISON: Old vs New System")
    print("=" * 60)
    
    print("\n❌ OLD KEYWORD-BASED SYSTEM (Supervisor-like):")
    print("   travel plan a trip to Paris")
    print("   calendar check my availability") 
    print("   expense what's my budget?")
    print("   smart organize a business trip")
    print("   → Required keywords = central dispatcher/supervisor")
    
    print("\n✅ NEW NATURAL LANGUAGE SYSTEM (True A2A):")
    print("   I want to plan a trip to Paris")
    print("   Check if I'm available next week")
    print("   What's my travel budget?") 
    print("   I need help organizing a business trip")
    print("   → Natural speech = intelligent agent coordination")
    
    print("\n🎯 KEY IMPROVEMENTS:")
    print("   • No keywords needed - just speak naturally")
    print("   • Interface Agent analyzes intent autonomously")
    print("   • Agents discover and coordinate peer-to-peer")
    print("   • True A2A spirit - no central supervisor")
    print("   • More intuitive and user-friendly")

if __name__ == "__main__":
    try:
        test_natural_language_analysis()
        show_comparison()
        
        print("\n\n🚀 Ready to test the full system!")
        print("Run: python multi_agent_travel.py")
        print("Then try: 'I want to plan a vacation to Italy'")
        
    except Exception as e:
        print(f"Error: {e}") 