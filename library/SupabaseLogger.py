"""
Supabase logging module for BME agent interactions.
Logs user/agent conversations to the Supabase `conversations` table.
"""

from supabase import create_client, Client
from typing import Optional


def get_supabase_client(url: str, key: str) -> Client:
    return create_client(url, key)


def log_interaction(
    client: Client,
    conversation_id: str,
    user_message: str,
    agent_response: str,
    user_id: Optional[str] = None
):
    """
    Log a single user/agent exchange to the conversations table.

    Args:
        client: Supabase client instance
        conversation_id: Mistral conversation ID
        user_message: The message sent by the user
        agent_response: The response returned by the agent
        user_id: Optional identifier for the user
    """
    row = {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "agent_response": agent_response,
        "user_id": user_id
    }
    client.table("conversations").insert(row).execute()
