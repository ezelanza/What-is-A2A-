#!/usr/bin/env python3
"""
Educational A2A Protocol Demo Launcher

Simple script to run the educational demonstration of A2A protocol.
Shows real agent-to-agent communication with proper JSON-RPC messages.
"""

import subprocess
import sys
import os

def main():
    print("🎓 Interactive A2A Protocol Educational Demo Launcher")
    print("=" * 52)
    print("Ask YOUR OWN question and see the ACTUAL A2A protocol in action!")
    print("Watch agents communicate to answer YOUR specific request!")
    print()
    
    # Check if Ollama is running
    print("🔍 Checking prerequisites...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434", timeout=2)
        print("✅ Ollama server is running")
    except:
        print("⚠️  Ollama server not detected")
        print("   Start it with: ollama serve")
        print("   Then install model: ollama pull llama3.2:3b")
        print("   (Demo will work without LLM, but with less intelligence)")
    
    # Check if educational demo exists
    if not os.path.exists("educational_a2a_demo.py"):
        print("❌ Educational demo not found in current directory")
        print("   Make sure you're in the What-is-A2A- folder")
        return
    
    print("✅ Educational demo ready")
    print()
    
    # Confirm to proceed
    proceed = input("🚀 Start educational A2A protocol demonstration? (y/n): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("Demo cancelled.")
        return
    
    print("\n🎓 Starting Interactive Educational A2A Protocol Demo...")
    print("📚 You'll ask a question and see how agents communicate with real A2A messages!")
    print("💬 Watch the complete flow from YOUR question to the final answer!")
    print()
    
    # Run the educational demo
    try:
        subprocess.run([sys.executable, "educational_a2a_demo.py"])
    except KeyboardInterrupt:
        print("\n👋 Educational demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("Try running directly: python educational_a2a_demo.py")

if __name__ == "__main__":
    main() 