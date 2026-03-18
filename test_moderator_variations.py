#!/usr/bin/env python3
"""
Test moderator with various message types to find inconsistent responses.
"""

import json
from library import ConversationManagement
from library.ConfigManager import config

# Get moderator agent ID
moderator_agent_id = config.get("moderator_agent")

# Test various message types
test_messages = [
    "hello",
    "How do robots work?",
    "My email is test@example.com",
    "What is BME?",
    "I have a question about sensors"
]

print("Testing moderator with various messages...")
print("=" * 60)

for i, message in enumerate(test_messages, 1):
    print(f"\nTest {i}: '{message}'")
    print("-" * 40)
    
    try:
        response = ConversationManagement.send_message_to_agent(
            message=message,
            agent_id=moderator_agent_id,
            conversation_id=None,
            display=False
        )
        
        assistant_response = response.get('assistant_response', '{}')
        print(f"Raw response: {assistant_response[:100]}...")  # Show first 100 chars
        
        # Try to parse
        if assistant_response.startswith('```json'):
            clean_response = assistant_response.replace('```json', '').replace('```', '').strip()
        else:
            clean_response = assistant_response
        
        try:
            data = json.loads(clean_response)
            status = data.get('status', 'MISSING')
            sanitized = data.get('sanitized_message', 'MISSING')
            reason = data.get('reason', 'MISSING')
            
            print(f"✅ Valid JSON: status={status}")
            print(f"   Sanitized: '{sanitized}'")
            print(f"   Reason: '{reason}'")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: {e}")
            print(f"   Response was: {repr(assistant_response[:200])}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")

print("\n" + "=" * 60)
print("Testing complete!")