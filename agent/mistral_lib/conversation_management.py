"""
Conversation management module for Mistral AI.
Provides functions to communicate with agents and manage conversations.
"""

from mistralai.client import Mistral
from typing import Optional, List, Dict, Any
import traceback
from shared_lib.config_manager import config
from shared_lib.logger import get_logger, log_debug, log_error, log_exception

# Initialize logger
logger = get_logger(__name__)


def _extract_text(value: Any) -> str:
    """Best-effort extraction of readable text from SDK response payloads."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [_extract_text(item) for item in value]
        return "\n".join([p for p in parts if p]).strip()
    if isinstance(value, dict):
        # Common text block shapes: {"type":"text","text":"..."} or {"content":"..."}
        for key in ("text", "content", "output_text", "value"):
            if key in value:
                return _extract_text(value.get(key))
        return ""

    # Pydantic-style models
    if hasattr(value, "model_dump"):
        try:
            return _extract_text(value.model_dump())
        except Exception:
            pass

    # Common object attributes
    for attr in ("text", "content"):
        if hasattr(value, attr):
            try:
                return _extract_text(getattr(value, attr))
            except Exception:
                pass

    return str(value)


def send_message_to_agent(
    message: str,
    api_key: Optional[str] = None,
    agent_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    display: bool = True,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Send a message to an agent and get the response.

    Args:
        message (str): The message/content to send to the agent
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided
        agent_id (str): The ID of the agent. Must be explicitly provided.
        conversation_id (str, optional): Existing conversation ID. If None, starts a new conversation
        display (bool, optional): If True, prints the conversation in a formatted way. Default: True

    Returns:
        dict: The conversation response containing agent's reply and conversation metadata

    Raises:
        Exception: If the API request fails

    Example:
        >>> # Send a message using default agent (starts new conversation)
        >>> response = send_message_to_agent("Hello, how can you help me with robots?")

        >>> # Continue an existing conversation
        >>> response = send_message_to_agent(
        ...     "Can you explain more about sensors?",
        ...     conversation_id="conv_123"
        ... )

        >>> # Override API key and agent ID
        >>> response = send_message_to_agent(
        ...     "What's your name?",
        ...     api_key="different_key",
        ...     agent_id="ag_456"
        ... )

        >>> # Get response without displaying
        >>> response = send_message_to_agent("Quick question", display=False)
    """
    # Use defaults from Configuration if not provided
    api_key = api_key or config.get("mistral_key")
    if agent_id is None:
        raise ValueError("agent_id must be explicitly provided")

    client = Mistral(api_key=api_key)

    try:
        # Prepare the message input
        inputs = [{"role": "user", "content": message}]

        # Prepare conversation parameters
        conversation_params = {
            "inputs": inputs
        }

        if debug:
            logger.debug("send_message_to_agent request", extra={
                "agent_id": agent_id,
                "conversation_id": conversation_id,
                "message": message
            })

        # Start or continue conversation
        if conversation_id:
            # Continue existing conversation
            response = client.beta.conversations.append(
                conversation_id=conversation_id,
                **conversation_params
            )
        else:
            # Start new conversation with the agent
            conversation_params["agent_id"] = agent_id
            response = client.beta.conversations.start(
                **conversation_params
            )

        # Extract useful information from response
        conversation_data = {
            'conversation_id': response.conversation_id,
            'agent_id': agent_id,
            'user_message': message,
            'assistant_response': '',
            'responding_agent_ids': [],
            'created_at': getattr(response, 'created_at', None),
            'updated_at': getattr(response, 'updated_at', None)
        }

        # Extract the assistant's response across SDK response shapes.
        assistant_text = ""

        if hasattr(response, 'output_text'):
            assistant_text = _extract_text(getattr(response, 'output_text'))

        if not assistant_text and hasattr(response, 'outputs') and response.outputs:
            for output in response.outputs:
                # Prefer message entries but tolerate shape variations.
                out_type = getattr(output, 'type', '')
                output_agent_id = getattr(output, 'agent_id', None)
                if output_agent_id and output_agent_id not in conversation_data['responding_agent_ids']:
                    conversation_data['responding_agent_ids'].append(output_agent_id)

                if hasattr(output, 'message'):
                    assistant_text = _extract_text(getattr(output.message, 'content', None))
                elif 'message' in str(out_type):
                    assistant_text = _extract_text(getattr(output, 'content', None))
                elif hasattr(output, 'content'):
                    assistant_text = _extract_text(getattr(output, 'content', None))

                if assistant_text:
                    break

        if not assistant_text and hasattr(response, 'choices') and response.choices:
            choice0 = response.choices[0]
            if hasattr(choice0, 'message'):
                assistant_text = _extract_text(getattr(choice0.message, 'content', None))

        if not assistant_text and hasattr(response, 'messages') and response.messages:
            for msg in response.messages:
                if getattr(msg, 'role', None) == 'assistant':
                    assistant_text = _extract_text(getattr(msg, 'content', None))
                    if assistant_text:
                        break

        conversation_data['assistant_response'] = assistant_text

        # Display the conversation if requested
        if display:
            print("\n" + "="*80)
            print("💬 CONVERSATION")
            print("="*80)
            print(f"🆔 Conversation ID: {conversation_data['conversation_id']}")
            print(f"🤖 Agent ID: {agent_id}")
            print(f"🕒 Created: {conversation_data['created_at']}")
            print("-" * 80)

            print(f"👤 User: {message}")
            print(f"🤖 Assistant: {conversation_data['assistant_response']}")

            print("="*80 + "\n")

        return conversation_data

    except Exception as e:
        if debug:
            logger.exception("send_message_to_agent exception", extra={
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "traceback": traceback.format_exc()
            })
            # Log additional exception attributes
            for attr in ("status_code", "code", "body", "response", "args"):
                if hasattr(e, attr):
                    try:
                        logger.debug(f"Exception attribute {attr}: {getattr(e, attr)}")
                    except Exception:
                        pass
        raise