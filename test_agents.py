#!/usr/bin/env python3
"""
Simple script to test both BME agents directly.
No complex structure - just send messages and print raw responses.
"""

import json
from library import ConversationManagement
from library.ConfigManager import config

# Test message - change this to test different inputs
test_message = "hello"

# Get agent IDs from configuration
bme_agent_id = config.get("bme_agent")
moderator_agent_id = config.get("moderator_agent", "ag_019cfce17e42754b86cf2a3eef28dd2b")  # Use the actual created agent ID

print(f"Testing agents with message: '{test_message}'")
print(f"BME Agent ID: {bme_agent_id}")
print(f"Moderator Agent ID: {moderator_agent_id}")
print("=" * 50)

# Test 1: Moderator Agent
print("\n1. TESTING MODERATOR AGENT")
print("-" * 30)
try:
    moderation_response = ConversationManagement.send_message_to_agent(
        message=test_message,
        agent_id=moderator_agent_id,
        conversation_id=None,
        display=False
    )
    print("✅ Moderator API call successful")
    print(f"Raw response: {moderation_response}")
    
    # Try to parse the JSON
    assistant_response = moderation_response.get('assistant_response', '{}')
    print(f"Assistant response: {assistant_response}")
    
    # Clean up Markdown code blocks if present
    if assistant_response.startswith('```json'):
        assistant_response = assistant_response.replace('```json', '').replace('```', '').strip()
    
    try:
        result_data = json.loads(assistant_response)
        print("✅ JSON parsing successful")
        print(f"Status: {result_data.get('status', 'NOT_FOUND')}")
        print(f"Reason: {result_data.get('reason', 'NOT_FOUND')}")
        print(f"Sanitized message: {result_data.get('sanitized_message', 'NOT_FOUND')}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print("This means the moderator is not returning proper JSON format")
        
except Exception as e:
    print(f"❌ Moderator API call failed: {e}")
    print("This could mean:")
    print("  - Invalid agent ID")
    print("  - API key issues")
    print("  - Network problems")

# Test 2: Main BME Agent
print("\n2. TESTING MAIN BME AGENT")
print("-" * 30)
try:
    bme_response = ConversationManagement.send_message_to_agent(
        message=test_message,
        agent_id=bme_agent_id,
        conversation_id=None,
        display=False
    )
    print("✅ BME Agent API call successful")
    print(f"Raw response: {bme_response}")
    assistant_response = bme_response.get('assistant_response', 'No response')
    print(f"Assistant response: {assistant_response}")
    
except Exception as e:
    print(f"❌ BME Agent API call failed: {e}")

print("\n" + "=" * 50)
print("TESTING COMPLETE")