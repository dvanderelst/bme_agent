"""
Agent management module for Mistral AI.
Provides functions to manage and update agents.
"""

from mistralai.client import Mistral
from typing import Optional, Union, List

import os
from shared_lib.config_manager import config


def agent_instructions(api_key: Optional[str] = None, agent_id: Optional[str] = None, new_instructions: Optional[str] = None):
    """
    Get or update the instructions for an existing Mistral AI agent.

    If new_instructions is provided, updates the agent instructions and creates a new version.
    If new_instructions is None, returns the current instructions without making changes.

    Args:
        api_key (str, optional): Your Mistral API key for authentication.
                                 If not provided, will use lib_secrets.mistral_key
        agent_id (str, optional): The ID of the agent you want to get/update.
                                If not provided, will use lib_secrets.agent_id
        new_instructions (str or file path, optional): The new instruction prompt for the agent
                                                    or path to a file containing instructions.
                                                    If None, only retrieves current instructions.
                                                    Can be:
                                                    - A string with direct instructions
                                                    - A filename (e.g., "main_agent.md") to load from agent_files/instructions/
                                                    - A full path to any instructions file

    Returns:
        Agent: If updating: The updated agent object containing version info and other metadata.
               If getting: The current agent object with instructions.

    Raises:
        Exception: If the API request fails
        FileNotFoundError: If the instructions file doesn't exist

    Examples:
        >>> # Get current instructions (using defaults from secrets.py)
        >>> agent = agent_instructions(api_key=api_key, agent_id=agent_id)
        >>> print(f"Current instructions: {agent.instructions}")

        >>> # Update instructions from string
        >>> result = agent_instructions(
        ...     api_key=api_key,
        ...     agent_id=agent_id,
        ...     new_instructions="You are a helpful AI assistant..."
        ... )
        >>> print(f"Updated to version {result.version}")

        >>> # Update instructions from file (using default instructions folder)
        >>> result = agent_instructions(
        ...     api_key=api_key,
        ...     agent_id=agent_id,
        ...     new_instructions="main_agent.md"  # Looks in agent_files/instructions/
        ... )
        >>> print(f"Updated to version {result.version}")

        >>> # Update instructions from file with full path
        >>> result = agent_instructions(
        ...     api_key=api_key,
        ...     agent_id=agent_id,
        ...     new_instructions="/full/path/to/instructions.txt"
        ... )
        >>> print(f"Updated to version {result.version}")

        >>> # Override defaults explicitly
        >>> result = agent_instructions(
        ...     api_key="different_key",
        ...     agent_id="different_agent",
        ...     new_instructions="Custom instructions"
        ... )
    """
    # API key can have a default, but agent_id must be explicitly provided
    api_key = api_key or config.get("mistral_key")
    if agent_id is None:
        raise ValueError("agent_id must be explicitly provided")

    # Initialize the Mistral client
    client = Mistral(api_key=api_key)

    # If no new instructions provided, just return current agent details
    if new_instructions is None:
        agent = client.beta.agents.get(agent_id=agent_id)
        return agent

    # Check if new_instructions is a file path
    instructions_file_path = None

    if isinstance(new_instructions, str):
        # If it's just a filename (no path), look in the default instructions folder
        if not os.path.isfile(new_instructions) and not os.path.isabs(new_instructions):
            # Try to find the file in the default instructions directory
            default_instructions_dir = os.path.join('agent_files', 'instructions')
            potential_path = os.path.join(default_instructions_dir, new_instructions)
            if os.path.isfile(potential_path):
                instructions_file_path = potential_path
        elif os.path.isfile(new_instructions):
            instructions_file_path = new_instructions

    if instructions_file_path:
        # Read instructions from file
        with open(instructions_file_path, 'r', encoding='utf-8') as f:
            instructions_content = f.read().strip()
    else:
        # Treat as direct instructions string
        instructions_content = str(new_instructions)

    # Prepare the update request
    update_request = {
        "instructions": instructions_content
    }

    # Send the update request to the API
    response = client.beta.agents.update(
        agent_id=agent_id,
        **update_request
    )

    return response


def set_agent_description(
    agent_id: Optional[str] = None,
    description: Optional[str] = None,
    api_key: Optional[str] = None
) -> bool:
    """
    Set the description for an agent.

    Args:
        agent_id (str, optional): The ID of the agent. Uses config.get("teacher_agent") if not provided
        description (str, optional): The description text to set for the agent
        api_key (str, optional): Your Mistral AI API key. Uses config.get("mistral_key") if not provided

    Returns:
        bool: True if description was set successfully

    Raises:
        ValueError: If description is empty or None
        Exception: If the API request fails

    Example:
        >>> success = set_agent_description(
        ...     agent_id="ag_123",
        ...     description="Robotics specialist for technical questions"
        ... )
    """
    # Use defaults from ConfigManager if not provided
    api_key = api_key or config.get("mistral_key")
    if agent_id is None:
        raise ValueError("agent_id must be explicitly provided")

    if not description:
        raise ValueError("Description cannot be empty")

    client = Mistral(api_key=api_key)

    client.beta.agents.update(
        agent_id=agent_id,
        description=description
    )
    return True


def unassign_all_libraries_from_agent(
    agent_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> bool:
    """
    Remove all libraries from an agent's accessible libraries.

    This is useful for cleaning up an agent's library access before reconfiguration
    or when you want to completely reset an agent's document access.

    Args:
        agent_id (str): The ID of the agent. Must be explicitly provided.
        api_key (str, optional): Your Mistral AI API key. Uses config.get("mistral_key") if not provided

    Returns:
        bool: True if all libraries were removed successfully

    Example:
        >>> # Clean up all library assignments from an agent
        >>> success = unassign_all_libraries_from_agent(agent_id="ag_123")
        >>> print(f"All libraries removed: {success}")

        >>> # Use with default agent
        >>> success = unassign_all_libraries_from_agent()
        >>> print(f"Cleaned up default agent libraries: {success}")
    """
    # Use defaults from ConfigManager if not provided
    api_key = api_key or config.get("mistral_key")
    if agent_id is None:
        raise ValueError("agent_id must be explicitly provided")

    client = Mistral(api_key=api_key)

    try:
        # Get current agent
        agent = client.beta.agents.get(agent_id=agent_id)

        # Find document_library tool
        tools = agent.tools if hasattr(agent, 'tools') and agent.tools else []
        library_tool = None

        for tool in tools:
            if hasattr(tool, 'type') and tool.type == 'document_library':
                library_tool = tool
                break

        if library_tool and hasattr(library_tool, 'library_ids'):
            # Remove the document_library tool entirely to unassign all libraries
            tools.remove(library_tool)

            # Update agent with new tools (without document_library)
            update_request = {
                "tools": tools
            }

            response = client.beta.agents.update(
                agent_id=agent_id,
                **update_request
            )

        return True


def assign_library_to_agent(
    library_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    level: str = "Viewer",
    api_key: Optional[str] = None
) -> bool:
    """
    Share a library with an agent by adding it to the agent's document_library tool.

    Args:
        library_id (str): The ID of the library to share
        agent_id (str, optional): The ID of the agent. Uses config.get("teacher_agent") if not provided
        level (str, optional): Access level ("Viewer" or "Editor"). Default: "Viewer"
        api_key (str, optional): Your Mistral AI API key. Uses config.get("mistral_key") if not provided

    Returns:
        bool: True if sharing was successful

    Raises:
        ValueError: If invalid access level is provided
        Exception: If the API request fails

    Example:
        >>> # Share a library with an agent (view-only access)
        >>> success = assign_library_to_agent(
        ...     library_id="lib_456",
        ...     agent_id="ag_123",
        ...     level="Viewer"
        ... )
        >>> print(f"Library shared: {success}")

        >>> # Share with edit access
        >>> success = assign_library_to_agent(
        ...     library_id="lib_789", 
        ...     agent_id="ag_123",
        ...     level="Editor"
        ... )
    """
    # Use defaults from ConfigManager if not provided
    api_key = api_key or config.get("mistral_key")
    if agent_id is None:
        raise ValueError("agent_id must be explicitly provided")
    if library_id is None:
        raise ValueError("library_id must be explicitly provided")

    # Validate access level (though it may not be used in this approach)
    valid_levels = ["Viewer", "Editor"]
    if level not in valid_levels:
        raise ValueError(f"Invalid access level: {level}. Must be one of: {valid_levels}")

    client = Mistral(api_key=api_key)

    try:
        # Get current agent
        agent = client.beta.agents.get(agent_id=agent_id)

        # Find or create document_library tool
        tools = agent.tools if hasattr(agent, 'tools') and agent.tools else []
        library_tool = None

        for tool in tools:
            if hasattr(tool, 'type') and tool.type == 'document_library':
                library_tool = tool
                break

        if library_tool:
            # Add to existing library_ids if not already present
            current_libs = getattr(library_tool, 'library_ids', [])
            if library_id not in current_libs:
                current_libs.append(library_id)
                library_tool.library_ids = current_libs
        else:
            # Create new document_library tool
            library_tool = {
                "type": "document_library",
                "library_ids": [library_id]
            }
            tools.append(library_tool)

        # Update agent with new tools
        update_request = {
            "tools": tools
        }

        response = client.beta.agents.update(
            agent_id=agent_id,
            **update_request
        )
        return True
