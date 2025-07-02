#!/usr/bin/env python3
"""
A2A Protocol Demo Runner
Convenience script to run both server and client
"""

import subprocess
import sys
import time
import signal
import threading
import os

def run_server():
    """Run the A2A agent server"""
    try:
        print("🚀 Starting A2A Agent Server...")
        server_process = subprocess.Popen([sys.executable, "a2a_agent_server.py"])
        return server_process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_client():
    """Run the A2A client after a delay"""
    print("⏳ Waiting for server to start...")
    time.sleep(2)  # Give server time to start
    
    try:
        print("🚀 Starting A2A Client...")
        subprocess.run([sys.executable, "a2a_client.py"])
    except Exception as e:
        print(f"❌ Failed to start client: {e}")

def main():
    """Main demo runner"""
    print("🤖 A2A Protocol Demo Runner")
    print("=" * 40)
    
    # Check if files exist
    if not os.path.exists("a2a_agent_server.py"):
        print("❌ a2a_agent_server.py not found!")
        return
    
    if not os.path.exists("a2a_client.py"):
        print("❌ a2a_client.py not found!")
        return
    
    server_process = None
    
    try:
        # Start server
        server_process = run_server()
        if not server_process:
            return
        
        # Start client in a separate thread so we can handle server cleanup
        client_thread = threading.Thread(target=run_client)
        client_thread.daemon = True
        client_thread.start()
        
        # Wait for client to finish
        client_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    
    finally:
        # Clean up server process
        if server_process:
            print("🧹 Cleaning up server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Server stopped")

if __name__ == "__main__":
    main() 