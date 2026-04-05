"""
Baserow logging module for BME agent interactions.
Logs user/agent conversations to a Baserow database table.
"""

import requests
import json
from typing import Optional, Dict, Any


def get_baserow_client(api_url: str, api_token: str) -> Dict[str, str]:
    """
    Create a Baserow client configuration dictionary.
    
    Args:
        api_url: The full Baserow API URL including table ID
        api_token: Baserow database token for authentication
        
    Returns:
        Dictionary containing API configuration
    """
    return {
        "api_url": api_url,
        "api_token": api_token
    }


def log_interaction(
    client_config: Dict[str, str],
    conversation_id: str,
    user_message: str,
    agent_response: str,
    user_id: Optional[str] = None
) -> bool:
    """
    Log a single user/agent exchange to the Baserow table.
    
    Args:
        client_config: Dictionary with 'api_url' and 'api_token'
        conversation_id: Mistral conversation ID
        user_message: The message sent by the user
        agent_response: The response returned by the agent
        user_id: Optional identifier for the user
        
    Returns:
        True if logging succeeded, False if failed
    """
    # Prepare the row data
    row_data = {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "agent_response": agent_response,
    }
    
    # Add user_id if provided
    if user_id is not None:
        row_data["user_id"] = user_id
    
    try:
        # Make the POST request to Baserow API
        # Add user_field_names=true to use field names instead of field IDs
        full_url = client_config["api_url"]
        if "?" in full_url:
            full_url += "&user_field_names=true"
        else:
            full_url += "?user_field_names=true"
            
        response = requests.post(
            url=full_url,
            headers={
                "Authorization": f"Token {client_config['api_token']}",
                "Content-Type": "application/json"
            },
            data=json.dumps(row_data),
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            return True
        else:
            # Log the error for debugging
            print(f"Baserow logging failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        # Handle network/connection errors
        print(f"Baserow logging error: {str(e)}")
        return False