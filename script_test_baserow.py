#!/usr/bin/env python3
"""
Test script for Baserow logger that writes dummy data using credentials from secrets.
This script tests the actual Baserow API connection.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import the baserow_logger
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared_lib.baserow_logger import get_baserow_client, log_interaction
from shared_lib.config_manager import config

def test_baserow_connection():
    """Test Baserow connection using credentials from secrets."""
    try:
        # Try to get credentials from Streamlit secrets first
        try:
            from streamlit import secrets as st_secrets
            baserow_config = get_baserow_client(
                st_secrets["baserow_api_url"], 
                st_secrets["baserow_api_token"]
            )
            print("✓ Using Streamlit secrets for Baserow credentials")
        except (ImportError, KeyError):
            # Fall back to config manager
            baserow_config = get_baserow_client(
                config.get("baserow_api_url"), 
                config.get("baserow_api_token")
            )
            print("✓ Using config manager for Baserow credentials")
        
        print(f"Connecting to Baserow at: {baserow_config['api_url']}")
        
        # Test data - create a few dummy conversations
        test_conversations = [
            {
                "conversation_id": "test_conv_001",
                "user_message": "What is biomimicry?",
                "agent_response": "Biomimicry is the design and production of materials, structures, and systems that are modeled on biological entities and processes.",
                "user_id": "student_001"
            },
            {
                "conversation_id": "test_conv_002",
                "user_message": "How do sensors work in medical devices?",
                "agent_response": "Medical sensors work by detecting physiological signals such as heart rate, blood pressure, or glucose levels, and converting them into electrical signals that can be processed and displayed.",
                "user_id": "student_002"
            },
            {
                "conversation_id": "test_conv_003",
                "user_message": "What are some examples of robotics in healthcare?",
                "agent_response": "Examples include surgical robots like the da Vinci system, rehabilitation robots for physical therapy, and robotic prosthetics that restore mobility to amputees.",
                "user_id": "student_003"
            }
        ]
        
        # Write each test conversation
        success_count = 0
        for i, conv in enumerate(test_conversations, 1):
            print(f"\nWriting test conversation {i}/{len(test_conversations)}...")
            
            success = log_interaction(
                client_config=baserow_config,
                conversation_id=conv["conversation_id"],
                user_message=conv["user_message"],
                agent_response=conv["agent_response"],
                user_id=conv["user_id"]
            )
            
            if success:
                success_count += 1
                print(f"✓ Successfully logged conversation {conv['conversation_id']}")
            else:
                print(f"✗ Failed to log conversation {conv['conversation_id']}")
        
        print(f"\n{'='*50}")
        print(f"Test Results: {success_count}/{len(test_conversations)} conversations logged successfully")
        
        if success_count == len(test_conversations):
            print("🎉 All test data written successfully!")
            return True
        else:
            print("⚠️  Some test data failed to write")
            return False
            
    except Exception as e:
        print(f"❌ Error during Baserow testing: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Baserow connection test...")
    print("="*50)
    
    success = test_baserow_connection()
    
    if success:
        print("\n✅ Baserow integration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Baserow integration test failed")
        sys.exit(1)