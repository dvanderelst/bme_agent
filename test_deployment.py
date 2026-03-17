#!/usr/bin/env python3
"""
Test script to verify all imports work for deployment.
"""

print("Testing deployment dependencies...")

try:
    # Test core imports
    import streamlit
    print("✅ Streamlit imported")
    
    from library import ConversationManagement
    print("✅ ConversationManagement imported")
    
    from library.SupabaseLogger import get_supabase_client
    print("✅ SupabaseLogger imported")
    
    from library.ConfigManager import config
    print("✅ ConfigManager imported")
    
    # Test mistralai import specifically
    from mistralai.client import Mistral
    print("✅ Mistral AI client imported")
    
    # Test configuration loading
    test_config = config.get("test_key", "default_value")
    print(f"✅ Configuration working: {test_config}")
    
    print("\n🎉 All deployment tests passed!")
    print("The app should work correctly when deployed to Streamlit.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install the missing package using: pip install <package>")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("Please check the error and fix the issue.")