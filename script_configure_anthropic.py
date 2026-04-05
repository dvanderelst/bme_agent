"""
Upload BME documents to the Anthropic Files API workspace.
Run this whenever the source documents change.
Files persist in the workspace until deleted — no need to re-upload on every run.
"""

import os
from anthropic_lib.file_management import upload_file, list_files, delete_file
from anthropic_lib.file_registry import save as save_registry
from shared_lib.output_logging import start_logging, stop_logging, OutputLogger
from shared_lib.config_manager import config

documents_dir = config.get("default_documents_dir") or os.path.join("agent_files", "documents")

documents = [
    "robot_details.md",
    "programming_blocks.md",
    "faculty_and_staff.md",
    "color_vision.md",
    "sonar.md",
]

start_logging("anthropic_configuration")
logger = OutputLogger()

##################################################################
logger.log_section("Anthropic Files API — Document Upload", level=1)
##################################################################

# Clear existing files in the workspace first
logger.log_section("Clearing Existing Files", level=2)
existing = list_files()
if existing:
    for f in existing:
        delete_file(f.id)
        logger.log(f"  🗑️  Deleted: {f.filename} ({f.id})")
    logger.log(f"  Removed {len(existing)} existing file(s)")
else:
    logger.log("  No existing files found")

# Upload fresh copies
logger.log_section("Uploading Documents", level=2)
uploaded = {}
for doc in documents:
    file_path = os.path.join(documents_dir, doc)
    file_id = upload_file(file_path)
    uploaded[doc] = file_id
    logger.log(f"  📄 {doc} → {file_id}")

logger.log_section("Summary", level=2)
logger.log(f"  ✅ {len(uploaded)} document(s) uploaded successfully")

# Persist file IDs to the registry
save_registry(uploaded)
logger.log("  📋 Registry written to anthropic_lib/file_registry.json")
for doc, file_id in uploaded.items():
    logger.log(f"    {doc}: {file_id}")

stop_logging()
