#!/usr/bin/env python3
"""
Test script for complete Zotero to Mistral workflow.
Downloads PDF from Zotero, uploads to Mistral library, and starts agent conversation.
"""

from library.ZoteroClient import create_zotero_client
from library.ConfigManager import get_zotero_agent, get_zotero_agent_library
from library.LibraryManagement import upload_document_and_wait, remove_all_documents_from_library
from library.AgentManagement import assign_library_to_agent
from library.ConversationManagement import send_message_to_agent

# Configuration
item_id = "AKMYITVM"
pdf_filename = "zotero_paper.pdf"
library_id = get_zotero_agent_library()
agent_id = get_zotero_agent()

# Step 1: Download from Zotero
print("📥 Step 1: Downloading PDF from Zotero")
zotero_client = create_zotero_client()
download_success = zotero_client.download_file(item_id, pdf_filename)
if not download_success: raise Exception("❌ Failed to download PDF from Zotero")

print("🗑️  Step 2: Clearing existing documents from library")
removed_count = remove_all_documents_from_library(library_id=library_id, confirm=False)
print(f"🗑️  Removed {removed_count} documents from library")

print("📤 Step 3: Uploading PDF to Mistral Library")
document = upload_document_and_wait(library_id=library_id, file_path=pdf_filename)

print("🤖 Step 4: Assigning Library to Agent")
success = assign_library_to_agent(library_id=library_id, agent_id=agent_id)

print("💬 Step 5: Starting Interactive Conversation")
conversation_id = None

# Initial message to analyze the paper
initial_message = "Analyze this paper about biosonar echoes"
response = send_message_to_agent(message=initial_message, agent_id=agent_id, conversation_id=conversation_id)
conversation_id = response['conversation_id']

# Interactive conversation loop
while True:
    user_input = input("👤 You: ").strip()
    
    if user_input.upper() == 'QUIT':
        print("👋 Goodbye!")
        break
    
    if user_input:
        response = send_message_to_agent(message=user_input, agent_id=agent_id, conversation_id=conversation_id, display=True)
        conversation_id = response['conversation_id']
