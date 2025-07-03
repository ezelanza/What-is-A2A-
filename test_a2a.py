#!/usr/bin/env python3
"""
Simple A2A SDK Test
==================

Test script to verify the official Google A2A SDK is working correctly.
"""

import a2a.types as a2a
import uuid

def test_a2a_components():
    """Test all A2A SDK components"""
    print("🧪 Testing A2A SDK Components...")
    
    # Test 1: AgentSkill creation
    print("\n1. Testing AgentSkill...")
    skill = a2a.AgentSkill(
        id="test_skill",
        name="Test Skill",
        description="A test skill for verification",
        tags=["test"],
        examples=["Test example"]
    )
    print(f"   ✅ Skill created: {skill.name}")
    
    # Test 2: AgentCard creation
    print("\n2. Testing AgentCard...")
    agent_card = a2a.AgentCard(
        name="Test Agent",
        description="A test agent for SDK verification",
        url="http://localhost:8001",
        version="1.0.0",
        capabilities=a2a.AgentCapabilities(streaming=False, pushNotifications=False),
        skills=[skill],
        defaultInputModes=["text"],
        defaultOutputModes=["text"]
    )
    print(f"   ✅ Agent Card created: {agent_card.name}")
    print(f"      URL: {agent_card.url}")
    print(f"      Skills: {len(agent_card.skills)}")
    
    # Test 3: Message creation
    print("\n3. Testing Message...")
    message = a2a.Message(
        messageId=str(uuid.uuid4()),
        role="user",
        parts=[a2a.TextPart(text="Hello A2A!")]
    )
    print(f"   ✅ Message created: {message.messageId[:8]}...")
    print(f"      Role: {message.role}")
    print(f"      Content: {message.parts[0].model_dump()['text']}")
    
    # Test 4: Task creation
    print("\n4. Testing Task...")
    task = a2a.Task(
        id=str(uuid.uuid4()),
        contextId=str(uuid.uuid4()),
        status=a2a.TaskStatus(state="submitted")
    )
    print(f"   ✅ Task created: {task.id[:8]}...")
    print(f"      Context: {task.contextId[:8]}...")
    print(f"      State: {task.status.state}")
    
    # Complete task
    task.status = a2a.TaskStatus(state="completed")
    print(f"   ✅ Task completed: {task.status.state}")
    
    print("\n🎉 ALL A2A SDK TESTS PASSED!")
    print("=" * 50)
    print("✅ AgentSkill: Working")
    print("✅ AgentCard: Working")
    print("✅ Message: Working")
    print("✅ Task: Working")
    print("✅ Official Google A2A SDK: Fully operational!")

if __name__ == "__main__":
    test_a2a_components()
