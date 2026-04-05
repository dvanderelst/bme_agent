"""
Configure both the Mistral and Anthropic agents in one pass.
Run this whenever the source documents or agent instructions change.
"""

import os
from mistral_lib import agent_management, library_management
from anthropic_lib.file_management import upload_file, list_files, delete_file
from anthropic_lib.file_registry import save as save_registry
from shared_lib.output_logging import start_logging, stop_logging, OutputLogger
from shared_lib.config_manager import config

# Shared document list — update here to affect both agents
documents = [
    "robot_details.md",
    "programming_blocks.md",
    "faculty_and_staff.md",
    "color_vision.md",
    "sonar.md",
    "olfaction.md",
    "touch_whiskers.md",
]

documents_dir = config.get("default_documents_dir") or os.path.join("agent_files", "documents")
bme_agent = config.get("bme_agent")
bme_agent_library = config.get("bme_agent_library")

start_logging("agent_configuration")
logger = OutputLogger()

##################################################################
logger.log_section("Mistral Agent Configuration", level=1)
##################################################################

logger.log_section("Agent Identifier", level=2)
logger.log(f"- Agent: {bme_agent}")

agent_management.agent_instructions(agent_id=bme_agent, new_instructions="bme_agent_instructions.md")
agent_management.set_agent_description(
    agent_id=bme_agent,
    description="Teaching and tech support agent for the Biology Meets Engineering (BME) high school program",
)
logger.log("✅ Agent configured successfully")

logger.log_section("Agent Library Configuration", level=2)
library_management.remove_all_documents_from_library(library_id=bme_agent_library, confirm=False)
for doc in documents:
    library_management.upload_document(doc, library_id=bme_agent_library)
    logger.log(f"  📄 Uploaded: {doc}")
agent_management.unassign_all_libraries_from_agent(agent_id=bme_agent)
agent_management.assign_library_to_agent(agent_id=bme_agent, library_id=bme_agent_library)
logger.log("🎉 Library configured successfully")

##################################################################
logger.log_section("Anthropic Files API — Document Upload", level=1)
##################################################################

logger.log_section("Clearing Existing Files", level=2)
existing = list_files()
if existing:
    for f in existing:
        delete_file(f.id)
        logger.log(f"  🗑️  Deleted: {f.filename} ({f.id})")
    logger.log(f"  Removed {len(existing)} existing file(s)")
else:
    logger.log("  No existing files found")

logger.log_section("Uploading Documents", level=2)
uploaded = {}
for doc in documents:
    file_path = os.path.join(documents_dir, doc)
    file_id = upload_file(file_path)
    uploaded[doc] = file_id
    logger.log(f"  📄 {doc} → {file_id}")

logger.log_section("Summary", level=2)
logger.log(f"  ✅ {len(uploaded)} document(s) uploaded successfully")

save_registry(uploaded)
logger.log("  📋 Registry written to anthropic_lib/file_registry.json")
for doc, file_id in uploaded.items():
    logger.log(f"    {doc}: {file_id}")

stop_logging()
