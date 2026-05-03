"""
Configure both the Mistral and Anthropic agents in one pass.

Before running, update DAILY_MODULES below to match today's activity.
Available modules: color_vision.md, sonar.md, olfaction.md, touch_whiskers.md
"""

import os
import re
import sys

import toml

from mistral_lib import agent_management, library_management
from anthropic_lib.file_management import upload_file, list_files, delete_file
from anthropic_lib.file_registry import save as save_registry
from shared_lib.output_logging import start_logging, stop_logging, OutputLogger
from shared_lib.config_manager import config

# ── UPDATE THIS BEFORE RUNNING ─────────────────────────────────────────────
daily_modules = ["olfaction.md"]
# ──────────────────────────────────────────────────────────────────────────

# ── Paths ──────────────────────────────────────────────────────────────────
documents_dir     = config.get("default_documents_dir")    or os.path.join("agent_files", "documents")
instructions_dir  = config.get("default_instructions_dir") or os.path.join("agent_files", "instructions")
activity_dir      = config.get("default_activity_dir")     or os.path.join("agent_files", "activity_descriptions")
instructions_path = os.path.join(instructions_dir, "bme_agent_instructions.md")
manifest_path     = os.path.join(documents_dir, "manifest.toml")

# ── Document selection ─────────────────────────────────────────────────────
shared_documents = [
    "robot_details.md",
    "programming_blocks.md",
    "faculty_and_staff.md",
]

documents = shared_documents + daily_modules

# ── Document metadata (single source of truth for both backends) ───────────
with open(manifest_path) as f:
    manifest = toml.load(f)

# Keyed by filename so lookups in the upload loops are direct.
metadata_by_file = {entry["file"]: entry for entry in manifest.values()}

missing = [d for d in documents if d not in metadata_by_file]
if missing:
    sys.exit(
        f"Manifest is missing entries for: {', '.join(missing)}. "
        f"Add them to {manifest_path}."
    )

# ── Agent IDs ──────────────────────────────────────────────────────────────
bme_agent         = config.get("bme_agent")
bme_agent_library = config.get("bme_agent_library")

start_logging("agent_configuration")
logger = OutputLogger()

##################################################################
logger.log_section("Today's Activity — Instructions Update", level=1)
##################################################################

activity_texts = []
for module in daily_modules:
    activity_path = os.path.join(activity_dir, module)
    if os.path.exists(activity_path):
        with open(activity_path) as f:
            activity_texts.append(f.read().strip())
        logger.log(f"  📖 Loaded activity description: {module}")
    else:
        logger.log(f"  ⚠️  No activity description found for: {module}")

if activity_texts:
    activity_text = "\n\n".join(activity_texts)
    with open(instructions_path) as f:
        instructions = f.read()
    updated = re.sub(
        r"(## Today's Activity\n).*?(\n## )",
        lambda m: m.group(1) + activity_text + "\n" + m.group(2),
        instructions,
        flags=re.DOTALL,
    )
    with open(instructions_path, "w") as f:
        f.write(updated)
    logger.log("  ✅ Instructions file updated")
else:
    logger.log("  ⚠️  No daily modules set — Today's Activity section unchanged")

##################################################################
logger.log_section("Mistral Agent Configuration", level=1)
##################################################################

logger.log_section("Agent Identifier", level=2)
logger.log(f"  Agent: {bme_agent}")

agent_management.agent_instructions(agent_id=bme_agent, new_instructions="bme_agent_instructions.md")
agent_management.set_agent_description(
    agent_id=bme_agent,
    description="Teaching and tech support agent for the Biology Meets Engineering (BME) high school program",
)
logger.log("  ✅ Agent configured successfully")

logger.log_section("Agent Library Configuration", level=2)
library_management.remove_all_documents_from_library(library_id=bme_agent_library, confirm=False)
for doc in documents:
    meta = metadata_by_file[doc]
    library_management.upload_document(
        doc, library_id=bme_agent_library, document_name=meta["title"]
    )
    logger.log(f"  📄 Uploaded: {doc} as {meta['title']!r}")

# Mistral has no per-doc description hook — roll the manifest descriptions
# into a single library description so the agent has an overview of what
# it's looking at.
library_overview = "\n".join(
    f"- {metadata_by_file[doc]['title']}: {metadata_by_file[doc]['description']}"
    for doc in documents
)
library_management.update_library_description(
    library_id=bme_agent_library,
    description=f"BME reference materials currently loaded:\n{library_overview}",
)
logger.log("  📝 Library description updated")

agent_management.unassign_all_libraries_from_agent(agent_id=bme_agent)
agent_management.assign_library_to_agent(agent_id=bme_agent, library_id=bme_agent_library)
logger.log("  🎉 Library configured successfully")

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
    meta = metadata_by_file[doc]
    uploaded[doc] = {
        "file_id":     file_id,
        "title":       meta["title"],
        "description": meta["description"],
    }
    logger.log(f"  📄 {doc} → {file_id}")

logger.log_section("Summary", level=2)
logger.log(f"  ✅ {len(uploaded)} document(s) uploaded successfully")
save_registry(uploaded)
logger.log("  📋 Registry written to anthropic_lib/file_registry.json")
for doc, entry in uploaded.items():
    logger.log(f"    {doc}: {entry['file_id']}")

# The previous file IDs were deleted from Anthropic above, so the
# committed registry on the remote is now pointing at IDs that no
# longer exist. Production won't get the new IDs until the regenerated
# file_registry.json is committed and pushed.
logger.log("")
logger.log("─" * 60)
logger.log("⚠️  Anthropic file IDs were rewritten.")
logger.log("    Commit and push anthropic_lib/file_registry.json so the")
logger.log("    deployed app references the new IDs — the old ones have")
logger.log("    been deleted from the Anthropic workspace.")
logger.log("─" * 60)

stop_logging()
