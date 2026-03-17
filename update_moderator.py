#!/usr/bin/env python3
"""
Quick script to update the moderator agent with corrected instructions.
"""

from library import AgentManagement
from library.ConfigManager import config

# Get the moderator agent ID
moderator_agent_id = config.get("moderator_agent", "ag_019cfce17e42754b86cf2a3eef28dd2b")

print(f"Updating moderator agent: {moderator_agent_id}")

# Update the instructions
AgentManagement.agent_instructions(
    agent_id=moderator_agent_id,
    new_instructions='agent_files/instructions/bme_moderator_instructions.md'
)

print("✅ Moderator agent instructions updated successfully!")
print("The agent should now return the original (sanitized) message instead of creating new responses.")