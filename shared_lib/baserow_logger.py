"""
Baserow logging module for BME agent interactions.
Logs user/agent conversations to a Baserow database table.
"""

import requests
import json
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urlunparse, parse_qs


def get_baserow_client(api_url: str, api_token: str) -> Dict[str, str]:
    """
    Create a Baserow client configuration dictionary.
    
    Args:
        api_url: The full Baserow API URL including table ID
        api_token: Baserow database token for authentication
        
    Returns:
        Dictionary containing API configuration
        
    Raises:
        ValueError: If api_url or api_token are empty
    """
    if not api_url or not api_token:
        raise ValueError("Baserow API URL and token must not be empty")
        
    if not api_url.startswith("https://"):
        raise ValueError("Baserow API URL must use HTTPS")
        
    return {
        "api_url": api_url,
        "api_token": api_token
    }


def add_query_param(url: str, param_name: str, param_value: str) -> str:
    """
    Add a query parameter to a URL using urllib.parse for robustness.
    
    Args:
        url: The base URL
        param_name: Query parameter name
        param_value: Query parameter value
        
    Returns:
        URL with the query parameter added
    """
    parsed = urlparse(url)
    query_dict = parse_qs(parsed.query, keep_blank_values=True)
    query_dict[param_name] = [param_value]
    new_query = '&'.join(f'{k}={v[0]}' for k, v in query_dict.items())
    return urlunparse(parsed._replace(query=new_query))


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
        # Validate input data lengths
        if len(user_message) > 10000:
            print("⚠️  User message exceeds maximum length (10000 characters)")
            return False
            
        if len(agent_response) > 10000:
            print("⚠️  Agent response exceeds maximum length (10000 characters)")
            return False
            
        # Add user_field_names=true to use field names instead of field IDs
        full_url = add_query_param(client_config["api_url"], "user_field_names", "true")
        
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
            # Enhanced error reporting
            error_msg = f"Baserow API error {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            
            # Try to provide helpful guidance for common errors
            if response.status_code == 401:
                print("🔑 Check your Baserow API token")
            elif response.status_code == 404:
                print("🔍 Check your table ID in the API URL")
            elif response.status_code == 422:
                print("📋 Check that all required fields exist in your Baserow table")
                
            return False
            
    except requests.exceptions.RequestException as e:
        # Handle network/connection errors with more detail
        error_type = type(e).__name__
        print(f"🌐 Network error ({error_type}): {str(e)}")
        
        if isinstance(e, requests.exceptions.Timeout):
            print("⏱️  Request timed out - check your internet connection")
        elif isinstance(e, requests.exceptions.ConnectionError):
            print("🔌 Connection failed - check if Baserow API is reachable")
            
        return False